import paramiko
from getpass import getpass

import json
from typing import Protocol

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from dknovautils import AT
from dknovautils import *

# pip install scp
from scp import SCPClient


def oswalk_simple_a(topdir: DkFile, topdown: bool = True) -> Iterator[DkFile]:
    """


    """
    assert topdown
    i = 0
    for _i, (root, dirs, files) in enumerate(os.walk(topdir.path, topdown=topdown)):
        yield topdir
        i += 1
        for d in dirs:
            dkf = DkFile(join(root, d))
            # yield dkf,i
            # i+=1
            yield from oswalk_simple_a(dkf, topdown=topdown)

        for d in itertools.chain(files):
            dkf = DkFile(join(root, d))
            yield dkf
            i += 1


@dataclass_json
@dataclass
class SimpleFileItem:
    file: DkFile
    name: str
    length: int
    path: str
    ext: str | None
    isNormalFile: bool
    mtime: int
    isDir: bool
    permission: int
    userid: int
    ext_lowercase: str | None
    file_ctt: bytes | None = None
    host: str | None = None
    idx: int = -1

    """
    
class SimpleFileItem(
    val file: File,
    val name: String,
    val idx: Int,
    val length: Long,
    val path: String,
    val ext: String? = null,
    val isNormalFile: Boolean,
    val mtime: Long,
    val isDir: Boolean,
) {

    val ext_lowercase: String? = ext?.lowercase()

    //    必要时 可以用来保存文件内容
    var file_ctt: ByteArray? = null
        
        
        
    """


def exec_ssh(
    ip: str,
    user: str,
    cmd: str,
    pwd: str,
    port: int = 22,
    sudopwd: str | None = None,
    verbose: bool = False,
) -> tuple[str, str]:

    cmd = cmd.strip()

    if verbose:
        iprint_debug(f"start cmd: {cmd}")

    startsudo = cmd.lower().startswith("sudo")

    if startsudo and not sudopwd:
        sudopwd = pwd

    sudocmd = startsudo

    get_pty = True if sudopwd else None

    # 建立连接
    trans = paramiko.Transport((ip, port))
    trans.connect(username=user, password=pwd)

    # 将sshclient的对象的transport指定为以上的trans
    ssh = paramiko.SSHClient()
    ssh._transport = trans

    # 剩下的就和上面一样了
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=get_pty)

    if sudocmd:

        if sudopwd:

            ssh_stdin.write(sudopwd + "\n")
            ssh_stdin.flush()
        else:

            AT.fail("err448")

    # if sudocmd and sudopwd:
    #     ssh_stdin.write(sudopwd + "\n")
    #     ssh_stdin.flush()

    # if sudopwd or cmd.startswith('sudo'):
    #     ssh_stdin.flush()

    outstr = str(ssh_stdout.read(), encoding="utf-8")
    errstr = str(ssh_stderr.read(), encoding="utf-8")

    # print(ssh_stdout.read())

    # 关闭连接
    trans.close()

    if verbose:
        iprint_debug(outstr)
        iprint_debug(f"end cmd: {cmd}")

    return outstr, errstr


@dataclass_json
@dataclass
class SSHConfig:
    ip: str
    user: str
    pwd: str
    port: int = 22

    def run_cmd(self, cmd: str, verbose: bool = False) -> tuple[str, str]:

        outstr, errstr = exec_ssh(
            ip=self.ip,
            user=self.user,
            cmd=cmd,
            pwd=self.pwd,
            port=self.port,
            sudopwd=self.pwd,
            verbose=verbose,
        )

        return outstr, errstr


class HomeLanUtils:

    @classmethod
    def parse_SimpleFileItem(cls, ln: str, idx: int = -1) -> SimpleFileItem:
        if False:
            # log.debug("parse line $ln")
            pass

        lnt = ln.strip()

        # y:f m:664 U:1000 T+:2024-11-01+02:34:13.7375737850 T@:1730399653.7375737850 secs s:309 bytes path:./.android/cache/sdkinf-1_029182a5-sys-img2-3_xml
        H = len("-rwxr-xr-x 2023-12-31 22:37:08.0000000000")

        lnps = lnt.split(" ")
        bs = int(lnps[4 + 2][2:])
        mtime = int(lnps[2 + 2][3:].split(".")[0]) * 1000
        bidx = lnt.find("path:")
        fpath = lnt[(bidx + len("path:")) :].strip()
        isdir = lnps[0][2:] == "d"
        permission = int(lnps[1][2:])
        userid = int(lnps[2][2:])

        assert lnps[0][2:] in ["f", "d"], f"err93125 bad file type: {ln}"

        dkf = DkFile(fpath)
        name = dkf.basename
        length = bs
        isNormalFile = True if not isdir else False
        isDir = not isNormalFile
        ext = dkf.extension[1:]
        ext_lowercase = ext.lower()

        sfi = SimpleFileItem(
            file=dkf,
            name=name,
            length=length,
            path=fpath,
            ext=ext,
            isNormalFile=isNormalFile,
            mtime=mtime,
            isDir=isDir,
            permission=permission,
            userid=userid,
            ext_lowercase=ext_lowercase,
        )

        return sfi

    BADSTR_kfnu = "Known file not used"

    @classmethod
    def ssh_traverse_dir(
        cls,
        sshcfg: SSHConfig,
        dirpath: str | None = None,
        cmd_part: str | None = None,
        cmd_grep: str | None = None,
        verbose: bool = False,
    ) -> List[SimpleFileItem]:  ##  #
        """
        val cmd4 =  find "$dir" -printf "%y %T+ %T@ secs %s bytes %p\n" | head -n $n  .trim()


        find . -printf "%y %T+ %T@ secs %s bytes %p\n"

        find . -printf "y:%y m:%m U:%U T+:%T+ T@:%T@ secs s:%s bytes path:%p\n" | head -n 100

        """

        _N = 10**9
        cmd_printf = (
            r' -printf "y:%y m:%m U:%U T+:%T+ T@:%T@ secs s:%s bytes path:%p\n" | head -n '
            + str(_N)
        )
        cmd_part = cmd_part if cmd_part else f'find "{dirpath}" '
        cmd4 = cmd_part + cmd_printf + ("" if not cmd_grep else f" | {cmd_grep} ")
        outstr, errstr = sshcfg.run_cmd(cmd=cmd4, verbose=verbose)
        return [cls.parse_SimpleFileItem(ln) for ln in outstr.strip().splitlines()]

        pass

    @classmethod
    def is_hashdeep_file(cls, ctt: str) -> bool:
        return "HASHDEEP" in ctt.splitlines()[0]

    @classmethod
    def hashdeep_output_passed(cls, stdout: str) -> bool:
        """
                    hashdeep 返回

        hashdeep: Audit passed
           Input files examined: 0
          Known files expecting: 0
                  Files matched: 12
        Files partially matched: 0
                    Files moved: 0
                New files found: 0
          Known files not found: 0


        """
        kw = "Audit passed"
        r = kw in stdout.strip().splitlines()[0]

        return r

    @classmethod
    def md5sum_output_passed(cls, stdout: str) -> bool:
        """
        xxxx: OK

        """
        kw = "OK"
        r = [ln for ln in stdout.strip().splitlines() if not ln.endswith(kw)]
        return r == []


@dataclass_json
@dataclass
class CheckRes:

    res: List[tuple[DkFile, int, str, str]] = field(default_factory=list)
    has_known_file_not_used: bool = False
    pass


def f_md5_check(dhome: str, verbose: bool = True):
    """

    find . -type f -name "*.mp3" > hd_files.list

    hashdeep -rl -f hd_files.list > hd_files.md5

    hashdeep -rl -a -vv -k ./hd_files.md5 -f hd_files.list

    如果hash找不到文件 则会打印如下内容
    ./Media/StarterContent.png: Known file not used

    如果windows中使用TC创建md5文件 必须设置 unicode保存 和 使用unix分隔符。

    md5sum 返回


    """

    def is_doublecmd_file(ctt: str) -> bool:
        return True

    assert AT.is_linux

    filesmd5 = [
        dfk
        for dfk in oswalk_simple_a(topdir=DkFile(dhome))
        if dfk.basename == "hd_files.md5"
    ]

    cr = CheckRes()

    for md5file in filesmd5:
        iprint_debug(f"md5file: {md5file}")

        ctt = Path(md5file.path).read_text(encoding="utf-8")

        if HomeLanUtils.is_hashdeep_file(ctt):

            cmdhash = "hashdeep -rl -a -vv -k hd_files.md5 -f hd_files.list"

            cmd = f'cd "{md5file.path.parent}" && {cmdhash}  '

            rcode, stdout, stderr = run_simple_b(cmd=cmd, verbose=verbose)
            cr.res.append((md5file, rcode, stdout, stderr))

            if HomeLanUtils.BADSTR_kfnu in stdout:
                cr.has_known_file_not_used = True

        else:

            cmdhash = "md5sum --check hd_files.md5 "

            cmd = f'cd "{md5file.path.parent}" && {cmdhash}  '

            rcode, stdout, stderr = run_simple_b(cmd=cmd, verbose=verbose)
            cr.res.append((md5file, rcode, stdout, stderr))

            # if BADSTR in stdout:
            #     cr.has_known_file_not_used = True

    return cr


"""




def faaa():
	assert is-linux
	参数	dhome为本地目录

	hd_files.md5

	遍历dhome目录，获取文件列表

	获取 hd_files.md5文件

		cd hddir
		md5hash ....
		
	class Res:
		...
		
		可以将运行结果打印输出到文件 方便持久化存储 作为数据日志来保存
			所以最好是pretty-json格式
			
	方便可以在sh中直接编写py脚本进行执行。
	初期用普通的文件遍历即可
	还要考虑与tc dc的结合问题
	后续会考虑支持hashdeep之类的工具等等
		
	返回 res



"""
