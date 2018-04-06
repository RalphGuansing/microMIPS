import xlwings
def Print_to_xlsx(cycle_array, code_line):
#    invoice = Invoice.objects.get(invoice_id = invoice_id)
#    components = Component.objects.filter(invoice = invoice)
    
    #USING MICROSOFT EXCEL xlsx
    wb = xlwings.Book('excelwriter.xlsx')
    sht = wb.sheets['Sheet1']
    

    row = 2
    
    nletter = 'A'
    letter = 'B'
    height = 13
    
    for nCtr, code in enumerate(code_line):
        cell = nletter +str(nCtr+row)
        sht.range(cell).value = str(nCtr)
        
        cell = letter +str(nCtr+row)
        sht.range(cell).value = code
    
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
    