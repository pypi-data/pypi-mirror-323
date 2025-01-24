# coding=utf-8

import re


class ExpressionString:

    def __init__(self, astr):
        self.segs = list()
        matchs = re.finditer(r'\$\{(.*?)\}', astr)
        start = 0
        for match in matchs:
            expression = match.group(1)
            self.segs.append((astr[start:match.start()], False, None))
            start = match.end()
            self.segs.append((expression, True, match.group()))
        self.segs.append((astr[start:len(astr)], False, None))
        pass

    def evaluate(self, env):
        segValues = list()
        for seg, isExpr, expression in self.segs:
            if isExpr:
                segValue = self.getExpressionFromEnv(env, seg)
                segValue = str(segValue) if segValue else expression
            else:
                segValue = seg
            segValues.append(segValue)
        return "".join(segValues)

    def getExpressionFromEnv(self, env, expression):
        dt = env
        for key in expression.split("."):
            dt = dt.get(key)
            if not dt:
                return None
        return dt
