"""
    DBus接口代码自动生成
"""
import os
import sys
import json
import yaml
import argparse
from lbkit.codegen.idf_interface import IdfInterface
from lbkit.utils.version import Version, X_VER

from mako.lookup import TemplateLookup
from lbkit.log import Logger
from lbkit.helper import Helper
from lbkit.errors import ArgException
from lbkit.misc import SmartFormatter

lb_cwd = os.path.split(os.path.realpath(__file__))[0]
log = Logger("codegen")

# 历史自动生成版本号，计划用于用于生成代码稳定性测试
# TODO： 支持生成代码稳定性测试，确保生成的代码一致性
history_versions = {
    "5.0": "简化枚举变更在接口间传递时的字符串定义"
}
__version__=Version("5.0")


def version_check(ver_str: str):
    ver = Version(ver_str)
    if history_versions.get(ver_str):
        return ver
    found = False
    if ver.minor == X_VER:
        major_str = str(ver.major) + "."
        for v, _ in history_versions.items():
            if v.startswith(major_str):
                found = True
                break
    if not found:
        log.error(f"Unkonw codegen version {ver_str}, supported versions:")
        for ver, msg in history_versions.items():
            log.error(f"    {ver}: {msg}")
        raise Exception("Unkonw codegen version get")
    return ver

class CodeGen(object):
    def __init__(self, args):
        self.args = args
        self.codegen_version = __version__

    def _gen(self, idf_file, directory="."):
        directory = os.path.realpath(directory)
        os.makedirs(os.path.join(directory, "public"), exist_ok=True)
        os.makedirs(os.path.join(directory, "server"), exist_ok=True)
        os.makedirs(os.path.join(directory, "client"), exist_ok=True)
        interface = self.get_interface(idf_file)
        out_file = os.path.join(directory, "public", interface.name + ".xml")
        interface.render_dbus_xml("interface.introspect.xml.mako", out_file)
        for code_type in ["server", "client", "public"]:
            out_file = os.path.join(directory, code_type, interface.name + ".h")
            interface.render_c_source(code_type + ".h.mako", out_file)
            out_file = os.path.join(directory, code_type, interface.name + ".c")
            interface.render_c_source(code_type + ".c.mako", out_file)
        json_file = os.path.join(directory, "package.yml")
        data = {
            "version": interface.version,
            "name": interface.name
        }
        with open(json_file, "w", encoding="utf-8") as fp:
            yaml.dump(data, fp, encoding='utf-8', allow_unicode=True)

        # 生成接口schema文件
        odf_file = os.path.join(directory, "server", "schema", f"{interface.name}.json")
        os.makedirs(os.path.dirname(odf_file), exist_ok=True)
        odf_data = interface.odf_schema
        with open(odf_file, "w", encoding="utf-8") as fp:
            json.dump(odf_data, fp, sort_keys=False, indent=4)

    def get_interface(self, idf_file):
        lookup = TemplateLookup(directories=os.path.join(lb_cwd, "template"))
        return IdfInterface(lookup, idf_file, self.codegen_version)

    def run(self):
        """
        代码自动生成.

        支持自动生成服务端和客户端C代码
        """
        parser = argparse.ArgumentParser(description=self.run.__doc__,
                                         prog="lbkit gen",
                                         formatter_class=SmartFormatter)
        # 默认的自动生成工具版本号为2
        parser.add_argument("-cv", "--codegen_version", help=f'''must less than or equal to {__version__.str}, default: {__version__.str}
                            format: major.version
                            for example: 1.3、2.4、3.3

                            description of changes:
                            4.x: compatible with lb_base/0.8.x
                            3.x: compatible with lb_base/0.7.x
                            2.x: compatible with lb_base/0.6.x
                            ''',
                            type=str, default=__version__.str)
        parser.add_argument("-d", "--directory", help='generate code directory', default=".")
        group2 = parser.add_argument_group('cdf file', 'Generate code using the specified CDF file')
        group2.add_argument("-c", "--cdf_file", help='component description file, default metadata/package.yml', default=None)
        group1 = parser.add_argument_group('idf file', 'Generate code using the specified IDF file')
        group1.add_argument("-i", "--idf_file", help='A IDF file to be processed e.g.: com.litebmc.Upgrade.xml', default=None)

        args = parser.parse_args(self.args)

        if args.cdf_file:
            if not os.path.isfile(args.cdf_file):
                raise ArgException(f"argument -c/--cdf_file: {args.cdf_file} not exist")
            configs = Helper.read_yaml(args.cdf_file, "codegen", [])
            # 为保障兼容，package.yml未指定版本号的，默认使用2，该版本配套lb_base/0.6.0版本，其LBProperty无set/get成员
            ver_str = Helper.read_yaml(args.cdf_file, "codegen_version", args.codegen_version)
            version_check(ver_str)
            self.codegen_version = Version(ver_str)
            for cfg in configs:
                file = cfg.get("file")
                if file is None:
                    log.error("%s的自动代码生成配置不正确, 缺少file元素指定描述文件", args.cdf_file)
                    sys.exit(-1)
                if not file.endswith(".yaml") :
                    log.error("%s的自动代码生成配置不正确, %s的文件名不是以.yaml结束", args.cdf_file, file)
                    sys.exit(-1)
                if not os.path.isfile(file):
                    log.error("%s的自动代码生成配置不正确, %s不是一个文件", args.cdf_file, file)
                    sys.exit(-1)
                outdir = cfg.get("outdir", os.getcwd())
                self._gen(file, outdir)
            return
        else:
            version_check(args.codegen_version)
            self.codegen_version = Version(args.codegen_version)

        intf_file = args.idf_file
        if not intf_file:
            raise ArgException(f"argument error, arguments -c/--cdf_file and -i/--idf_file are not set")
        if not os.path.isfile(intf_file):
            raise ArgException(f"argument -i/--idf_file: {args.idf_file} not exist")
        if self.codegen_version.bt(__version__.str):
            raise ArgException(f"argument -cv/--codegen_version: validate failed, must less than or equal to {__version__.str}")
        out_dir = os.path.join(os.getcwd(), args.directory)
        if not intf_file.endswith(".yaml"):
            raise ArgException(f"The IDF file ({intf_file}) not endswith .yaml")
        if  not os.path.isfile(intf_file):
            raise ArgException(f"The IDF file ({intf_file}) not exist")
        if not os.path.isdir(out_dir):
            log.warning(f"Directory {args.directory} not exist, try create")
            os.makedirs(out_dir)
        self._gen(intf_file, out_dir)

if __name__ == "__main__":
    gen = CodeGen(sys.argv)
    gen._gen("com.litebmc.test.xml", ".")
