# coding=utf-8
import re
import os

import yaml

import utils.expression as expression


def load(file):
    conf = {}
    with open(file, "r") as input:
        conf = yaml.load(input, Loader=yaml.SafeLoader)
        pass
    env = dict(os.environ)
    env.update(conf)
    replaceStringExpression(env, conf)
    return conf


def replaceStringExpression(env, obj):
    result = obj
    if type(obj) is dict:
        for key, value in obj.items():
            obj[key] = replaceStringExpression(env, value)
    elif type(obj) is list:
        for idx, value in enumerate(obj):
            obj[idx] = replaceStringExpression(env, value)
    else:
        if type(obj) is str:
            result = obj if obj.find(
                "${") == -1 else expression.ExpressionString(obj).evaluate(env)
    return result
