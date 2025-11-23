# Outlook OOO Days Counter - Instructions

This VBA macro helps you quickly count all-day "OOO" (Out of Office) appointments in your Outlook calendar over any date range.

## Installation Instructions

### Step 1: Enable Developer Tab in Outlook
1. Open Outlook
2. Go to **File** → **Options** → **Customize Ribbon**
3. On the right side, check the box next to **Developer**
4. Click **OK**

### Step 2: Import the Macro
1. In Outlook, click on the **Developer** tab
2. Click **Visual Basic** (or press Alt+F11)
3. In the VBA Editor, go to **File** → **Import File**
4. Browse to and select `OutlookOOOCounter.bas`
5. The module should now appear in your Project Explorer

**Alternative - Manual Entry:**
1. In the VBA Editor, go to **Insert** → **Module**
2. Open the `OutlookOOOCounter.bas` file in a text editor
3. Copy all the code and paste it into the new module

### Step 3: Enable Macros (if needed)
1. Go to **File** → **Options** → **Trust Center** → **Trust Center Settings**
2. Click on **Macro Settings**
3. Select **Notifications for digitally signed macros, all other macros disabled** or **Enable all macros** (less secure but easier)
4. Click **OK**

## Usage

You have three macros to choose from:

### 1. `CountOOODays` (Recommended)
**What it does:** Prompts you for a start and end date, then counts total OOO days.

**How to run:**
1. Press **Alt+F8** in Outlook
2. Select `CountOOODays` from the list
3. Click **Run**
4. Enter your start date (e.g., 01/01/2024)
5. Enter your end date (e.g., 12/31/2024)
6. View the results in a popup message

### 2. `CountOOODaysQuick`
**What it does:** Instantly counts OOO days for the current calendar year without prompting.

**How to run:**
1. Press **Alt+F8** in Outlook
2. Select `CountOOODaysQuick`
3. Click **Run**
4. View the results immediately

### 3. `ListOOODaysDetailed`
**What it does:** Shows a detailed breakdown of each OOO period with dates and day counts.

**How to run:**
1. Press **Alt+F8** in Outlook
2. Select `ListOOODaysDetailed`
3. Click **Run**
4. Enter your date range
5. View the detailed list

## Optional: Create a Quick Access Button

To run the macro with a single click:

1. In Outlook, go to **File** → **Options** → **Quick Access Toolbar**
2. In the "Choose commands from" dropdown, select **Macros**
3. Find your macro (e.g., `CountOOODaysQuick`)
4. Click **Add >>**
5. Click **OK**

Now you'll have a button on your Quick Access Toolbar to run the macro instantly!

## Optional: Assign a Keyboard Shortcut

Unfortunately, Outlook doesn't have a built-in way to assign keyboard shortcuts to macros. However, you can:

1. Create a custom ribbon button (more complex)
2. Use the Quick Access Toolbar button and press Alt + [number] to activate it

## Customization

### Change the Search Term
If you use something other than "OOO" for your appointments, modify this line in the code:

```vb
If olAppt.AllDayEvent = True And InStr(1, olAppt.Subject, "OOO", vbTextCompare) > 0 Then
```

Change `"OOO"` to your preferred term (e.g., `"Vacation"`, `"PTO"`, etc.)

### Search Multiple Terms
To search for multiple terms (e.g., "OOO" or "PTO" or "Vacation"), replace the line above with:

```vb
If olAppt.AllDayEvent = True And _
   (InStr(1, olAppt.Subject, "OOO", vbTextCompare) > 0 Or _
    InStr(1, olAppt.Subject, "PTO", vbTextCompare) > 0 Or _
    InStr(1, olAppt.Subject, "Vacation", vbTextCompare) > 0) Then
```

### Change Default Date Range
In `CountOOODays`, modify these lines to change the default suggested dates:

```vb
startDate = DateSerial(Year(Date), 1, 1)  ' January 1 of current year
endDate = DateSerial(Year(Date), 12, 31)  ' December 31 of current year
```

Examples:
- Last 12 months: `startDate = DateAdd("m", -12, Date)`
- Last 365 days: `startDate = DateAdd("d", -365, Date)`
- Specific date: `startDate = #1/1/2024#`

## Troubleshooting

**Problem:** "Compile error: User-defined type not defined"
- **Solution:** In VBA Editor, go to **Tools** → **References** and check **Microsoft Outlook XX.0 Object Library**

**Problem:** Macro doesn't find any appointments
- **Solution:** 
  - Verify your appointments are titled exactly "OOO" (case-insensitive)
  - Ensure they are marked as "All Day Event"
  - Check that the date range includes your appointments

**Problem:** Count seems wrong for multi-day appointments
- **Solution:** This is likely correct! Outlook stores the end date of all-day events as midnight of the day *after* the last day. The macro accounts for this correctly.

**Problem:** Security warning about running macros
- **Solution:** Click "Enable Macros" or adjust your macro security settings (see Step 3 above)

## How It Works

The macro:
1. Accesses your default Outlook calendar
2. Filters appointments within your specified date range
3. Looks for all-day appointments with "OOO" in the subject (case-insensitive)
4. For multi-day appointments, calculates the number of days using the start and end dates
5. Sums up all the days and displays the result

**Note on multi-day events:** When you create a 3-day appointment (e.g., Monday-Wednesday), Outlook stores the end date as Thursday at midnight. The macro uses `DateDiff` to calculate the correct number of days.

## Example Output

```
OOO Days Summary

Date Range: 01/01/2024 to 12/31/2024
Total OOO Days: 23

This includes all all-day appointments with 'OOO' in the title.
```

## Advanced: Export to Excel

If you want to export the results to Excel for further analysis, let me know and I can provide an enhanced version that creates a spreadsheet with detailed breakdowns!

## Support

If you encounter any issues or want to customize the macro further, feel free to ask!

