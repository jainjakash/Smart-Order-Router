import sys
import time
import thread
import argparse
import quickfix as fix
from tools.echo import echo
from collections import OrderedDict	
import xlrd


class Application(fix.Application):
    orderID = 0
    execID = 0

    bids = {}
    asks = {}
    #creates empty dictionaries

    loc = ("C:\\Bloomberg\\SampleMarketData.xlsx")
    wb = xlrd.open_workbook(loc)
    sheetMSFT = wb.sheet_by_index(0)
    sheetNFLX = wb.sheet_by_index(1)
    sheetNames = wb.sheet_names()

    xl_sheet1 = wb.sheet_by_index(0)
    xl_sheet2 = wb.sheet_by_index(1)

    sheet1Name = xl_sheet1.name.encode("utf-8")
    sheet2Name = xl_sheet2.name.encode("utf-8")

    excelbids = {}
    excelbids['BATS'] = {}
    excelbids['BATS'][sheet1Name] = {}
    excelbids['BATS'][sheet2Name] = {}
    excelbids['NASD'] = {}
    excelbids['NASD'][sheet1Name] = {}
    excelbids['NASD'][sheet2Name] = {}
    excelasks = {}
    excelasks['BATS'] = {}
    excelasks['BATS'][sheet1Name] = {}
    excelasks['BATS'][sheet2Name] = {}
    excelasks['NASD'] = {}
    excelasks['NASD'][sheet1Name] = {}
    excelasks['NASD'][sheet2Name] = {}

    for i in range (2, 7):
		for j in range (0, 1):
			excelbids['NASD'][sheet1Name][sheetMSFT.cell_value(i, j)] = sheetMSFT.cell_value(i, j+1)

    for i in range (2, 7):
		for j in range (2, 3):
			excelasks['NASD'][sheet1Name][sheetMSFT.cell_value(i, j)] = sheetMSFT.cell_value(i, j+1)

    for i in range (9, 14):
		for j in range (0, 1):
			excelbids['BATS'][sheet1Name][sheetMSFT.cell_value(i, j)] = sheetMSFT.cell_value(i, j+1)

    for i in range (9, 14):
		for j in range (2, 3):
			excelasks['BATS'][sheet1Name][sheetMSFT.cell_value(i, j)] = sheetMSFT.cell_value(i, j+1)

    for i in range (2, 7):
		for j in range (0, 1):
			excelbids['NASD'][sheet2Name][sheetNFLX.cell_value(i, j)] = sheetNFLX.cell_value(i, j+1)

    for i in range (2, 7):
		for j in range (2, 3):
			excelasks['NASD'][sheet2Name][sheetNFLX.cell_value(i, j)] = sheetNFLX.cell_value(i, j+1)

    for i in range (9, 14):
		for j in range (0, 1):
			excelbids['BATS'][sheet2Name][sheetNFLX.cell_value(i, j)] = sheetNFLX.cell_value(i, j+1)

    for i in range (9, 14):
		for j in range (2, 3):
			excelasks['BATS'][sheet2Name][sheetNFLX.cell_value(i, j)] = sheetNFLX.cell_value(i, j+1)
   
   #reads excel files, inputs data into nested dictionaries

    @echo
    def onCreate(self, sessionID): return
    @echo
    def onLogon(self, sessionID): return
    @echo
    def onLogout(self, sessionID): return
    @echo
    def toAdmin(self, sessionID, message): return
    @echo
    def fromAdmin(self, sessionID, message): return
    @echo
    def toApp(self, sessionID, message): return
    @echo
    def fromApp(self, message, sessionID):
		beginString = fix.BeginString()
		msgType = fix.MsgType()
		message.getHeader().getField( beginString )
		message.getHeader().getField( msgType )


		if msgType.getValue() == 'F':
			print ('Cancel Request')
			symbol = fix.Symbol()
			side = fix.Side()
			clOrdID = fix.ClOrdID()
			origClOrdID = fix.OrigClOrdID()
			orderQty = fix.OrderQty()

			message.getField( orderQty )
			message.getField( clOrdID )
			message.getField( origClOrdID )
			message.getField( symbol )
			message.getField( side )

			executionReport = fix.Message()
			executionReport.getHeader().setField( beginString )
			executionReport.getHeader().setField( fix.MsgType(fix.MsgType_ExecutionReport) )
			executionReport.setField( symbol )
			executionReport.setField( side )
			executionReport.setField( clOrdID )
			executionReport.setField( origClOrdID )
			executionReport.setField( fix.ExecID(self.genExecID()) )
			executionReport.setField( fix.OrderID(self.genOrderID()) )
			executionReport.setField( fix.AvgPx(0))
			executionReport.setField( fix.LastShares(0))
			executionReport.setField( fix.CumQty(0))

			if beginString.getValue() == fix.BeginString_FIX40 or beginString.getValue() == fix.BeginString_FIX41 or beginString.getValue() == fix.BeginString_FIX42:
				executionReport.setField( fix.ExecTransType(fix.ExecTransType_CANCEL) )
			executionReport.setField( fix.OrdStatus(fix.OrdStatus_CANCELED) )

			if beginString.getValue() >= fix.BeginString_FIX41:
				executionReport.setField( fix.ExecType(fix.ExecType_CANCELED) )
				executionReport.setField( fix.LeavesQty(0) )
			else:
				executionReport.setField( fix.ExecType(fix.ExecType_CANCELED) )
				executionReport.setField( fix.LeavesQty(0) )

			try:
				print executionReport
				fix.Session.sendToTarget( executionReport, sessionID )
			except SessionNotFound, e:
				return



		if msgType.getValue() == 'D':
			print 'New Order Single'
		
			symbol = fix.Symbol()
			side = fix.Side()
			ordType = fix.OrdType()
			orderQty = fix.OrderQty()
			price = fix.Price()
			timeInForce = fix.TimeInForce()

			clOrdID = fix.ClOrdID()
			message.getField( ordType )
			print message
			
			if ordType.getValue() == fix.OrdType_LIMIT:
				message.getField( price )
				price = round(float(price.getValue()),2)
			
			message.getField( symbol )
			message.getField( side )
			message.getField( orderQty )
			message.getField( clOrdID )
			message.getField( timeInForce )

			

			executionReport = fix.Message()
			executionReport.getHeader().setField( beginString )
			executionReport.getHeader().setField( fix.MsgType(fix.MsgType_ExecutionReport) )

			availableQty = 0
			if side.getValue() == '2':
				#check the bids
				sym = symbol.getValue()
				mergedDict = sorted(set(self.excelbids['BATS'][sym].keys()) | set(self.excelbids['NASD'][sym].keys()), reverse = True)
				orderMergedDict = OrderedDict()
				for pricelevel in mergedDict:
					orderMergedDict[pricelevel] = OrderedDict()
					if pricelevel in self.excelbids['BATS'][sym].keys():	 
						orderMergedDict[pricelevel]['BATS'] = self.excelbids['BATS'][sym][pricelevel]
					if pricelevel in self.excelbids['NASD'][sym].keys():
						orderMergedDict[pricelevel]['NASD'] = self.excelbids['NASD'][sym][pricelevel]
				print '-------------Sell Order - Checking available Bids-------------'
				qty = orderQty.getValue()
				orderToSend = {}
				for bid_price, exch in orderMergedDict.iteritems():
					if price <= bid_price or ordType.getValue() == fix.OrdType_MARKET :
						for exchange,bid_qty in exch.iteritems():
							if exchange not in orderToSend:
								orderToSend[exchange] = {}
							if bid_qty >= qty and qty > 0:
								orderToSend[exchange][bid_price] = qty
								qty = 0
							elif qty > 0:
								orderToSend[exchange][bid_price] = bid_qty
								qty = qty - bid_qty
							availableQty += bid_qty
				
			else:
				#check the asks
				sym = symbol.getValue()
				mergedDict = sorted(set(self.excelasks['BATS'][sym].keys()) | set(self.excelasks['NASD'][sym].keys()))
				orderMergedDict = OrderedDict()
				for pricelevel in mergedDict:
					orderMergedDict[pricelevel] = OrderedDict()
					if pricelevel in self.excelasks['BATS'][sym].keys():	 
						orderMergedDict[pricelevel]['BATS'] = self.excelasks['BATS'][sym][pricelevel]
					if pricelevel in self.excelasks['NASD'][sym].keys():
						orderMergedDict[pricelevel]['NASD'] = self.excelasks['NASD'][sym][pricelevel]
				print '--------------Buy Order - Checking available Asks-------------'
				qty = orderQty.getValue()
				orderToSend = {}
				for ask_price, exch in orderMergedDict.iteritems():
					#if ask_price <= round(float(price.getValue()),2):
					if ask_price <= price or ordType.getValue() == fix.OrdType_MARKET:
						for exchange,ask_qty in exch.iteritems():
							if exchange not in orderToSend:
								orderToSend[exchange] = {}
							if ask_qty >= qty and qty > 0:
								orderToSend[exchange][ask_price] = qty
								qty = 0
							elif qty > 0:
								orderToSend[exchange][ask_price] = ask_qty
								qty = qty - ask_qty
							availableQty += ask_qty

			filledQty = 0
			if len(orderToSend) > 0:
				for exchange, detailsOfOrders in orderToSend.iteritems():
					for price, qty in detailsOfOrders.iteritems():
						filledQty = filledQty + qty
						executionReport.setField( fix.OrderID(self.genOrderID()) )
						executionReport.setField( fix.ExecID(self.genExecID()) )
						if filledQty >= orderQty.getValue():
							executionReport.setField( fix.OrdStatus(fix.OrdStatus_FILLED) )
						else:
							executionReport.setField( fix.OrdStatus(fix.OrdStatus_PARTIALLY_FILLED) )
						executionReport.setField( symbol )
						executionReport.setField( side )
						executionReport.setField( fix.CumQty(filledQty))
						executionReport.setField( fix.AvgPx(price )) # to do - need to properly calculate average price
						executionReport.setField( fix.LastShares(qty))
						executionReport.setField( fix.LastPx(price))
						executionReport.setField( clOrdID )
						executionReport.setField( orderQty )
						executionReport.setField( fix.LastMkt(exchange))

						if beginString.getValue() == fix.BeginString_FIX40 or beginString.getValue() == fix.BeginString_FIX41 or beginString.getValue() == fix.BeginString_FIX42:
							executionReport.setField( fix.ExecTransType(fix.ExecTransType_NEW) )

						if beginString.getValue() >= fix.BeginString_FIX41:
							if filledQty >=0 :
								executionReport.setField( fix.ExecType(fix.ExecType_FILL) )
								executionReport.setField( fix.LeavesQty(0) )
							else:
								executionReport.setField( fix.ExecType(fix.ExecType_PARTIAL_FILL) )
								executionReport.setField( fix.LeavesQty(orderQty.getValue() - filledQty) )

						try:
							print executionReport
							fix.Session.sendToTarget( executionReport, sessionID )
						except SessionNotFound, e:
							return

			if timeInForce.getValue() == fix.TimeInForce_IMMEDIATE_OR_CANCEL:
				print "TimeInForce is IOC - need to cancel the remaining balance"
				executionReport = fix.Message()
				executionReport.getHeader().setField( beginString )
				executionReport.getHeader().setField( fix.MsgType(fix.MsgType_ExecutionReport) )
				executionReport.setField( symbol )
				executionReport.setField( side )
				executionReport.setField( clOrdID )
				executionReport.setField( fix.ExecID(self.genExecID()) )
				executionReport.setField( fix.OrderID(self.genOrderID()) )
				executionReport.setField( fix.AvgPx(price))
				executionReport.setField( fix.LastShares(0))
				executionReport.setField( fix.CumQty(filledQty))
				executionReport.setField( fix.LastPx(price))
				executionReport.setField( orderQty )

				if beginString.getValue() == fix.BeginString_FIX40 or beginString.getValue() == fix.BeginString_FIX41 or beginString.getValue() == fix.BeginString_FIX42:
					executionReport.setField( fix.ExecTransType(fix.ExecTransType_CANCEL) )
				executionReport.setField( fix.OrdStatus(fix.OrdStatus_CANCELED) )

				if beginString.getValue() >= fix.BeginString_FIX41:
					executionReport.setField( fix.ExecType(fix.ExecType_CANCELED) )
					executionReport.setField( fix.LeavesQty(0) )
				else:
					executionReport.setField( fix.ExecType(fix.ExecType_CANCELED) )
					executionReport.setField( fix.LeavesQty(0) )

				try:
					print executionReport
					fix.Session.sendToTarget( executionReport, sessionID )
				except SessionNotFound, e:
					return

				

    def genOrderID(self):
    	self.orderID = self.orderID+1
    	return `self.orderID`
    def genExecID(self):
    	self.execID = self.execID+1
    	return `self.execID`

def main(file_name):

    try:
        settings = fix.SessionSettings(file_name)
        application = Application()
        storeFactory = fix.FileStoreFactory( settings )
        logFactory = fix.FileLogFactory( settings )
        print 'creating acceptor'
        acceptor = fix.SocketAcceptor( application, storeFactory, settings, logFactory )
        print 'starting acceptor'
        acceptor.start()

        while 1:
            time.sleep(1)
    except (fix.ConfigError, fix.RuntimeError), e:
        print e

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='FIX Server')
    parser.add_argument('file_name', type=str, help='Name of configuration file')
    args = parser.parse_args()
    main(args.file_name)
