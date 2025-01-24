# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2024/12/9 23:53
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi import builder, view, compiler, rfc1902


class SnmpObject:
    def __init__(self, ipaddr, port=161, community="public"):
        # self.snmpEngine = SnmpEngine()
        self.ipaddr = ipaddr
        self.port = port
        self.community = community

    def deal_value(self, oid, value, prettyPrint):
        # print(" = ".join([x.prettyPrint() for x in (oid, value)]))
        print(f"\n{oid.prettyPrint()} = {value}")
        print(f"类型为：{type(value).__name__}")

        expect_rule = value.subtypeSpec
        sub_expect_rule = expect_rule[-1]
        try:
            sub_expect_rule(value)
        except Exception as e:  # ValueConstraintError
            raise Exception(f"{oid.prettyPrint()}返回值不符合预期范围|返回值的范围为{sub_expect_rule},实际却为{value}")

        if prettyPrint:
            return value.prettyPrint()
        elif isinstance(value, Integer32):
            return int(value)
        elif isinstance(value, OctetString):
            print('octet')
            print(str(value))
            return value.prettyPrint()
        else:
            print('else')
            return value.prettyPrint()

    def deal_error(self, errorIndication, errorStatus, errorIndex, varBinds):
        if errorIndication:
            raise Exception("snmp 响应发生错误:", errorIndication)
        elif errorStatus:
            # print(
            #     f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1][0] if errorIndex else '?'}"
            # )
            if varBinds:
                raise Exception("%s at %s" % (errorStatus.prettyPrint(),
                                              errorIndex and varBinds[int(errorIndex) - 1][0] or "?",))
            else:
                raise Exception("%s at %s" % (errorStatus.prettyPrint(), str(varBinds)))
        else:
            pass

    async def get_cmd_single(self, oid, prettyPrint=False):
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint)
            print(result)
            return result

    async def get_cmd_single_mib(self, object_type, index=0, mib_name="NTCIP1203v03f-MIB", prettyPrint=False):
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity(mib_name, object_type, index))
        )

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint)
            # print(result)
            return result

    async def get_cmd_many(self, *varBinds, prettyPrint=False):
        # print(content)
        resultList = []
        iterator = get_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            *varBinds
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            if "fontStatus" in oid.prettyPrint():
                result = self.deal_value(oid, value, True)
            else:
                result = self.deal_value(oid, value, prettyPrint)
            resultList.append(result)
        return resultList

    async def set_cmd(self, oid, value, prettyPrint=False):
        if isinstance(value, int):
            value = Integer32(value)
        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid), value)
        )
        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint)
            print(result)
            return result

    async def set_cmd_single_mib(self, object_type, value, index=1, mib_name="NTCIP1203v03f-MIB", prettyPrint=False,
                                 check_value=False):
        if isinstance(value, int):
            value = Integer32(value)

        if check_value:
            from pysnmp.smi import builder, view, compiler
            mibBuilder = builder.MibBuilder()
            mibViewController = view.MibViewController(mibBuilder)
            compiler.add_mib_compiler(
                mibBuilder,
                sources=["file:///usr/share/snmp/mibs"],
            )
            mibBuilder.load_modules("NTCIP1203v03f-MIB")
            mib_obj = ObjectType(ObjectIdentity(mib_name, object_type, index), value).\
                resolve_with_mib(mibViewController)

            expect_rule = mib_obj[1].subtypeSpec
            sub_expect_rule = expect_rule[-1]
            try:
                sub_expect_rule(mib_obj[1])
            except Exception as e:  # ValueConstraintError
                raise Exception(f"返回值的范围为{sub_expect_rule},实际却为{mib_obj[1]}")

        else:
            mib_obj = ObjectType(ObjectIdentity(mib_name, object_type, index), value)

        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            mib_obj
        )

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint)
            print(result)
            return result

    async def next_cmd_single_mib(self, object_type, index=0, mib_name="NTCIP1203v03f-MIB", prettyPrint=False):
        errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=1),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity(mib_name, object_type, index)),
            # lexicographicMode=True,
        )

        self.deal_error(errorIndication, errorStatus, errorIndex, varBinds)

        for oid, value in varBinds:
            result = self.deal_value(oid, value, prettyPrint)
            print(result)
            # return result

    async def bulk_cmd(self, nonRepeaters, maxRepetitions, *varBinds, prettyPrint=False):
        resultList = []
        errorIndication, errorStatus, errorIndex, varBindTable = await bulk_cmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=1),
            await UdpTransportTarget.create((self.ipaddr, self.port)),
            ContextData(),
            nonRepeaters, maxRepetitions,
            *varBinds
        )

        self.deal_error(errorIndication, errorStatus, errorIndex, varBindTable)

        for oid, value in varBindTable:
            result = self.deal_value(oid, value, prettyPrint)
            resultList.append(result)

        print(resultList)
        return resultList


if __name__ == "__main__":
    snmpObject = SnmpObject("192.168.1.105")
    # asyncio.run(snmpObject.get_cmd_many([
    #     ObjectType(ObjectIdentity("1.3.6.1.4.1.1206.4.2.3.3.1.0")),
    #     ObjectType(ObjectIdentity("1.3.6.1.4.1.1206.4.2.3.6.8.0"))]))
    # asyncio.run(snmpObject.get_cmd_single("1.3.6.1.4.1.1206.4.2.3.3.1.0"))
    # 字体名称
    # print("返回",asyncio.run(snmpObject.get_cmd_single("1.3.6.1.4.1.1206.4.2.3.3.2.1.3.3")))
    # asyncio.run(snmpObject.set_cmd("1.3.6.1.4.1.1206.4.2.3.6.1.0",4))
    # result = asyncio.run(snmpObject.get_cmd_single("1.3.6.1.4.1.1206.4.2.3.6.1.0"))
    # print("result: ", result)
