$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$wb = $excel.Workbooks.Open('C:\Users\llll\Documents\두인경매\바이브코딩\data\지하철역1(위례과천선포함).xlsx')
$wb.SaveAs('C:\Users\llll\Documents\두인경매\바이브코딩\scratch\subway.csv', 6)
$wb.Close($false)
$excel.Quit()
