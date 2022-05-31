from pymodbus.client.sync import ModbusTcpClient

PLC_IP = "192.168.12.55"

client = ModbusTcpClient(PLC_IP)
#a = client.read_holding_registers(0,4)
#print(a.registers[0])
client.write_register(0, 0x0)
#b = client.read_holding_registers(2,1)
#print(b.registers[0])