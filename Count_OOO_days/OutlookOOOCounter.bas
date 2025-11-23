Sub CountOOODays()
    ' This macro counts all-day appointments titled "OOO" in your calendar
    ' over a specified date range
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.Namespace
    Dim olCalendar As Outlook.Folder
    Dim olItems As Outlook.Items
    Dim olAppt As Outlook.AppointmentItem
    Dim startDate As Date
    Dim endDate As Date
    Dim totalDays As Long
    Dim filterStr As String
    Dim resultMsg As String
    
    ' Initialize
    Set olApp = Outlook.Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    Set olCalendar = olNamespace.GetDefaultFolder(olFolderCalendar)
    
    ' Set date range (modify these as needed)
    ' Example: Count for current calendar year
    startDate = DateSerial(Year(Date), 1, 1)
    endDate = DateSerial(Year(Date), 12, 31)
    
    ' Or prompt user for date range
    Dim userStart As String
    Dim userEnd As String
    
    userStart = InputBox("Enter start date (MM/DD/YYYY):", "Start Date", Format(startDate, "mm/dd/yyyy"))
    If userStart = "" Then Exit Sub
    startDate = CDate(userStart)
    
    userEnd = InputBox("Enter end date (MM/DD/YYYY):", "End Date", Format(endDate, "mm/dd/yyyy"))
    If userEnd = "" Then Exit Sub
    endDate = CDate(userEnd)
    
    ' Create filter for date range
    filterStr = "[Start] >= '" & Format(startDate, "mm/dd/yyyy") & "' AND [Start] <= '" & Format(endDate, "mm/dd/yyyy") & "'"
    
    ' Apply filter and sort
    Set olItems = olCalendar.Items
    olItems.Sort "[Start]", False
    olItems.IncludeRecurrences = True
    Set olItems = olItems.Restrict(filterStr)
    
    ' Initialize counter
    totalDays = 0
    
    ' Loop through appointments
    For Each olAppt In olItems
        ' Check if it's an all-day appointment with "OOO" in the subject
        If olAppt.AllDayEvent = True And InStr(1, olAppt.Subject, "OOO", vbTextCompare) > 0 Then
            ' Calculate number of days for this appointment
            ' For all-day events, End date is at midnight of the day after
            Dim dayCount As Long
            dayCount = DateDiff("d", olAppt.Start, olAppt.End)
            totalDays = totalDays + dayCount
        End If
    Next olAppt
    
    ' Display results
    resultMsg = "OOO Days Summary" & vbCrLf & vbCrLf
    resultMsg = resultMsg & "Date Range: " & Format(startDate, "mm/dd/yyyy") & " to " & Format(endDate, "mm/dd/yyyy") & vbCrLf
    resultMsg = resultMsg & "Total OOO Days: " & totalDays & vbCrLf & vbCrLf
    resultMsg = resultMsg & "This includes all all-day appointments with 'OOO' in the title."
    
    MsgBox resultMsg, vbInformation, "OOO Days Counter"
    
    ' Clean up
    Set olAppt = Nothing
    Set olItems = Nothing
    Set olCalendar = Nothing
    Set olNamespace = Nothing
    Set olApp = Nothing
End Sub


Sub CountOOODaysQuick()
    ' Quick version - counts OOO days for the current calendar year
    ' without prompting for dates
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.Namespace
    Dim olCalendar As Outlook.Folder
    Dim olItems As Outlook.Items
    Dim olAppt As Outlook.AppointmentItem
    Dim startDate As Date
    Dim endDate As Date
    Dim totalDays As Long
    Dim filterStr As String
    
    ' Set to current calendar year
    startDate = DateSerial(Year(Date), 1, 1)
    endDate = DateSerial(Year(Date), 12, 31)
    
    Set olApp = Outlook.Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    Set olCalendar = olNamespace.GetDefaultFolder(olFolderCalendar)
    
    filterStr = "[Start] >= '" & Format(startDate, "mm/dd/yyyy") & "' AND [Start] <= '" & Format(endDate, "mm/dd/yyyy") & "'"
    
    Set olItems = olCalendar.Items
    olItems.Sort "[Start]", False
    olItems.IncludeRecurrences = True
    Set olItems = olItems.Restrict(filterStr)
    
    totalDays = 0
    
    For Each olAppt In olItems
        If olAppt.AllDayEvent = True And InStr(1, olAppt.Subject, "OOO", vbTextCompare) > 0 Then
            totalDays = totalDays + DateDiff("d", olAppt.Start, olAppt.End)
        End If
    Next olAppt
    
    MsgBox "Total OOO days in " & Year(Date) & ": " & totalDays, vbInformation, "OOO Counter"
    
    Set olAppt = Nothing
    Set olItems = Nothing
    Set olCalendar = Nothing
    Set olNamespace = Nothing
    Set olApp = Nothing
End Sub


Sub ListOOODaysDetailed()
    ' This version shows a detailed list of all OOO appointments
    
    Dim olApp As Outlook.Application
    Dim olNamespace As Outlook.Namespace
    Dim olCalendar As Outlook.Folder
    Dim olItems As Outlook.Items
    Dim olAppt As Outlook.AppointmentItem
    Dim startDate As Date
    Dim endDate As Date
    Dim totalDays As Long
    Dim filterStr As String
    Dim resultMsg As String
    
    startDate = DateSerial(Year(Date), 1, 1)
    endDate = DateSerial(Year(Date), 12, 31)
    
    Dim userStart As String
    Dim userEnd As String
    
    userStart = InputBox("Enter start date (MM/DD/YYYY):", "Start Date", Format(startDate, "mm/dd/yyyy"))
    If userStart = "" Then Exit Sub
    startDate = CDate(userStart)
    
    userEnd = InputBox("Enter end date (MM/DD/YYYY):", "End Date", Format(endDate, "mm/dd/yyyy"))
    If userEnd = "" Then Exit Sub
    endDate = CDate(userEnd)
    
    Set olApp = Outlook.Application
    Set olNamespace = olApp.GetNamespace("MAPI")
    Set olCalendar = olNamespace.GetDefaultFolder(olFolderCalendar)
    
    filterStr = "[Start] >= '" & Format(startDate, "mm/dd/yyyy") & "' AND [Start] <= '" & Format(endDate, "mm/dd/yyyy") & "'"
    
    Set olItems = olCalendar.Items
    olItems.Sort "[Start]", False
    olItems.IncludeRecurrences = True
    Set olItems = olItems.Restrict(filterStr)
    
    totalDays = 0
    resultMsg = "OOO Days Detail" & vbCrLf & String(50, "-") & vbCrLf
    
    For Each olAppt In olItems
        If olAppt.AllDayEvent = True And InStr(1, olAppt.Subject, "OOO", vbTextCompare) > 0 Then
            Dim dayCount As Long
            dayCount = DateDiff("d", olAppt.Start, olAppt.End)
            totalDays = totalDays + dayCount
            
            resultMsg = resultMsg & Format(olAppt.Start, "mm/dd/yyyy") & " to " & _
                        Format(olAppt.End - 1, "mm/dd/yyyy") & " (" & dayCount & " day"
            If dayCount > 1 Then resultMsg = resultMsg & "s"
            resultMsg = resultMsg & ")" & vbCrLf
        End If
    Next olAppt
    
    resultMsg = resultMsg & String(50, "-") & vbCrLf
    resultMsg = resultMsg & "Total: " & totalDays & " days"
    
    MsgBox resultMsg, vbInformation, "OOO Days Detailed List"
    
    Set olAppt = Nothing
    Set olItems = Nothing
    Set olCalendar = Nothing
    Set olNamespace = Nothing
    Set olApp = Nothing
End Sub

