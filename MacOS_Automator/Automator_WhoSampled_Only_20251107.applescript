
on run {input, parameters}
	-- Activate Tidal
	tell application "Tidal"
		activate
	end tell
	
	delay 0.5
	
	-- Prompt user to copy the Twitter share link
	display dialog "1. Right-click the now-playing track" & return & "2. Click 'Share' > 'X (Twitter)'" & return & "3. Copy the URL from your browser" & return & "4. Click OK" buttons {"OK"}
	
	-- Get the URL from clipboard
	set shareURL to (the clipboard)
	
	set name_ to ""
	set artist_ to ""
	
	-- Try to extract from URL
	if shareURL contains "text=" then
		-- Extract the text parameter
		set textStart to offset of "text=" in shareURL
		set textPart to text (textStart + 5) through -1 of shareURL
		-- Find the end of the text parameter (either & or end of string)
		set textEnd to offset of "&" in textPart
		if textEnd > 0 then
			set textPart to text 1 through (textEnd - 1) of textPart
		end if
		
		-- Decode URL-encoded characters
		set textPart to replace_text(textPart, "%20", " ")
		set textPart to replace_text(textPart, "%27", "'")
		set textPart to replace_text(textPart, "%21", "!")
		set textPart to replace_text(textPart, "%22", "\"")
		set textPart to replace_text(textPart, "%26", "&")
		set textPart to replace_text(textPart, "%2B", "+")
		set textPart to replace_text(textPart, "%3D", "=")
		set textPart to replace_text(textPart, "%3F", "?")
		set textPart to replace_text(textPart, "%0A", " ")
		set textPart to replace_text(textPart, "%0D", " ")
		set textPart to replace_text(textPart, "%3A", ":")
		set textPart to replace_text(textPart, "%2F", "/")
		set textPart to replace_text(textPart, "%23", "#")
		set textPart to replace_text(textPart, "%5B", "[")
		set textPart to replace_text(textPart, "%5D", "]")
		set textPart to replace_text(textPart, "%7B", "{")
		set textPart to replace_text(textPart, "%7D", "}")
		set textPart to replace_text(textPart, "%25", "%")
		
		-- Parse "Listen to [TRACK] by [ARTIST]" format
		if textPart contains "Listen to" and textPart contains " by " then
			-- Extract track: between "Listen to " and " by "
			set listenStart to offset of "Listen to " in textPart
			set byPos to offset of " by " in textPart
			set name_ to text (listenStart + 10) through (byPos - 1) of textPart
			
			-- Extract artist: after " by "
			set artist_ to text (byPos + 4) through -1 of textPart
			
			-- Remove any URLs or extra text after artist
			if artist_ contains "http" then
				set httpPos to offset of "http" in artist_
				set artist_ to text 1 through (httpPos - 1) of artist_
			end if
			
			-- Trim whitespace from both artist and track
			set artist_ to trim_spaces(artist_)
			set name_ to trim_spaces(name_)
		end if
	end if
	
	-- If parsing failed, prompt user
	if name_ is "" or artist_ is "" then
		display dialog "Couldn't parse URL. Please enter manually:" buttons {"OK"}
		set artist_ to text returned of (display dialog "Artist name:" default answer "")
		set name_ to text returned of (display dialog "Track name:" default answer "")
	else
		display dialog "Found:" & return & "Artist: " & artist_ & return & "Track: " & name_ buttons {"OK", "Edit"} default button "OK"
		if button returned of result is "Edit" then
			set artist_ to text returned of (display dialog "Artist name:" default answer artist_)
			set name_ to text returned of (display dialog "Track name:" default answer name_)
		end if
	end if
	
	-- Create hyphenated versions for WhoSampled (convert spaces to hyphens)
	set artist_hyphen to replace_text(artist_, " ", "-")
	set name_hyphen to replace_text(name_, " ", "-")
	
	-- Construct WhoSampled URL
	set whosampled_url to "https://www.whosampled.com/" & artist_hyphen & "/" & name_hyphen & "/"
	
	-- Display URL for verification
	display dialog "Opening WhoSampled:" & return & whosampled_url buttons {"OK"}
	
	-- Open URL in Safari
	tell application "Safari"
		activate
		open location whosampled_url
	end tell
	
	return input
end run

-- Helper function to replace text
on replace_text(thisText, searchString, replaceString)
	set AppleScript's text item delimiters to searchString
	set textItems to text items of thisText
	set AppleScript's text item delimiters to replaceString
	set thisText to textItems as string
	set AppleScript's text item delimiters to ""
	return thisText
end replace_text

-- Helper function to trim spaces
on trim_spaces(thisText)
	-- Remove leading spaces
	repeat while thisText starts with " "
		set thisText to text 2 through -1 of thisText
	end repeat
	
	-- Remove trailing spaces
	repeat while thisText ends with " "
		set thisText to text 1 through -2 of thisText
	end repeat
	
	return thisText
end trim_spaces

