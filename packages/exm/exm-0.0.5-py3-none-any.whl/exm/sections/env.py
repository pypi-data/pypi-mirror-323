# coding=utf-8
import os


def process(conf, ctx):
    env = dict(os.environ)
    env.update(conf["env"])
    ctx["env"] = env
