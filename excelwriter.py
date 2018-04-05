import xlwings
def Print_to_xlsx(cycle_array):
#    invoice = Invoice.objects.get(invoice_id = invoice_id)
#    components = Component.objects.filter(invoice = invoice)
    
    #USING MICROSOFT EXCEL xlsx
    wb = xlwings.Book(r'C:\Users\Ralph\Documents\GitHub\microMIPS\excelwriter.xlsx')
    sht = wb.sheets['Sheet1']
    
#    #charged to
#    sht.range('B1').value = invoice.buyer.name
#    #address
#    sht.range('B7').value = invoice.address
#    #date
#    sht.range('G1').value = invoice.date
#    #term
#    sht.range('G3').value = invoice.term
#    #agent
#    sht.range('G5').value = invoice.seller.name
    
#    #CLEAR previous components#
#    row = 10
#    for num in range(0,8):
#        cell = 'A' + str(row+1)
#        sht.range(cell).value = ""
#        row = row+1
    
    #WRITE current components#
    row = 2
    
    height = 13
#    total_amount = 0
    letter = 'C'
    for cycle in cycle_array:
        
        
        for i in range(0, height):
            cell = letter + str(row+i)
            if i in cycle:
                sht.range(cell).value = cycle[i]
            else:
                sht.range(cell).value = ""
        
        
        
        letter = chr(ord(letter) + 1)
    
    wb.save()
    #wb.close()
    