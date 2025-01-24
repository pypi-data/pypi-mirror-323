import configparser
import logging
import os
import sys

log = logging.getLogger('EConfig')

class EConfig :

    configs= {}

    @classmethod
    def getConfig(cls, config_file_name='app.ini'):
        if config_file_name not in cls.configs:
            rootPath = cls._getConfigRootPath(cls.getEnv())
            cls.configs[config_file_name] = configparser.ConfigParser()
            cls.configs[config_file_name].read(rootPath + config_file_name)

        return cls.configs[config_file_name]

    @classmethod
    def getEnv(cls):
        if os.environ.get('ENV') is None:
            return 'dev'
        env = os.environ.get('ENV')

        if env not in ['dev', 'test', 'prod']:
            raise ValueError(f"ENV {env} is not supported")
        else :
            return env

    @classmethod
    def clearConfigCache(cls):
        cls.configs.clear()

    @classmethod
    def _getConfigRootPath(cls, env):
        #获取进程启动的系统路径
        root_path = sys.path[0]
        return root_path + '/config/' + env + '/'
    