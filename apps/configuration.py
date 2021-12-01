#auther:"l"
#date:2019/5/25

import os
import configparser

# 项目路径
rootDir = os.path.split(os.path.realpath(__file__))[0]
# config.ini文件路径
configFilePath = os.path.join(rootDir, 'config.ini')

def get_config_values(section, option):

    """
    根据传入的section获取对应的value
    :param section: ini配置文件中用[]标识的内容
    :return:
    """
    config = configparser.ConfigParser()
    config.read(configFilePath)
    # return config.items(section=section)
    return config.get(section=section, option=option)


if __name__ == '__main__':
    result = int(get_config_values('mysql', 'port'))
    print(result)