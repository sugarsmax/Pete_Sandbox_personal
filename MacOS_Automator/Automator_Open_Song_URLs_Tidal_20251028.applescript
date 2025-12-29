
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
	
	-- Parse the URL to extract artist and track
	-- Twitter share URLs look like: https://twitter.com/intent/tweet?text=Track%20-%20Artist%20on%20%40TIDAL&url=...
	-- or the clipboard might have the full track info
	
	set name_ to ""
	set artist_ to ""
	
	-- Try to extract from URL
	if shareURL contains "text=" then
		-- Extract the text parameter
		set textStart to offset of "text=" in shareURL
		set textPart to text (textStart + 5) through -1 of shareURL
		set textEnd to offset of "&" in textPart
		if textEnd > 0 then
			set textPart to text 1 through (textEnd - 1) of textPart
		end if
		
		-- Decode URL-encoded characters
		set textPart to replace_text(textPart, "%20", " ")
		set textPart to replace_text(textPart, "%0A", " ")
		set textPart to replace_text(textPart, "%3A", ":")
		set textPart to replace_text(textPart, "%2F", "/")
		
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
		
		-- Extract the direct Tidal track URL if present
		if shareURL contains "https%3A%2F%2Ftidal.com%2Ftrack%2F" then
			set tidal_URL to replace_text(shareURL, "%3A", ":")
			set tidal_URL to replace_text(tidal_URL, "%2F", "/")
			-- Find the start of the Tidal URL
			set tidalStart to offset of "https://tidal.com/track/" in tidal_URL
			if tidalStart > 0 then
				set tidal_URL_raw to text tidalStart through -1 of tidal_URL
				-- Get just the URL part (stop at & or end)
				set ampPos to offset of "&" in tidal_URL_raw
				if ampPos > 0 then
					set tidal_URL to text 1 through (ampPos - 1) of tidal_URL_raw
				else
					set tidal_URL to tidal_URL_raw
				end if
				set tidal_URL to word 1 of tidal_URL  -- Get first word to remove any trailing chars
			end if
		end if
	end if
	
	-- If parsing failed, prompt user
	if name_ is "" or artist_ is "" then
		display dialog "Couldn't parse URL. Please enter manually:" buttons {"OK"}
		set artistInput to text returned of (display dialog "Artist name:" default answer "")
		set trackInput to text returned of (display dialog "Track name:" default answer "")
		set name_ to trackInput
		set artist_ to artistInput
	else
		display dialog "Found:" & return & artist_ & " - " & name_ buttons {"OK", "Edit"} default button "OK"
		if button returned of result is "Edit" then
			set artistInput to text returned of (display dialog "Artist name:" default answer artist_)
			set trackInput to text returned of (display dialog "Track name:" default answer name_)
			set name_ to trackInput
			set artist_ to artistInput
		end if
	end if
	
	-- Create underscore versions for other URLs and hyphenated versions for WhoSampled
	set AppleScript's text item delimiters to " "
	set artist_underscore to (text items of artist_) as string
	set artist_hyphen to (text items of artist_) as string
	set AppleScript's text item delimiters to "_"
	set artist_underscore to artist_underscore as string
	set AppleScript's text item delimiters to "-"
	set artist_hyphen to artist_hyphen as string

	set AppleScript's text item delimiters to " "
	set name_underscore to (text items of name_) as string
	set name_hyphen to (text items of name_) as string
	set AppleScript's text item delimiters to "_"
	set name_underscore to name_underscore as string
	set AppleScript's text item delimiters to "-"
	set name_hyphen to name_hyphen as string
	
	-- Construct URLs 
	set tidal_URL to "https://tidal.com/search?q=" & artist_ & " " & name_
	set spotify_URL to "https://open.spotify.com/search/" & name_
	set lastfm_my_top to "https://www.last.fm/user/sugarsmax/library/music/" & artist_ & "/+tracks"
	set lastfm_all_top to "https://www.last.fm/music/" & artist_ & "/+tracks?date_preset=ALL#top-tracks"
	set youtube_url to "https://www.youtube.com/results?search_query=" & artist_ & " " & name_
	set whosampled_url to "https://www.whosampled.com/" & artist_hyphen & "/" & name_hyphen

	-- Open all URLs in Chrome
	tell application "Google Chrome"
		activate
		open location tidal_URL
		open location spotify_URL
		open location lastfm_my_top
		open location lastfm_all_top
		open location youtube_url
        open location whosampled_url
	end tell
	
	return input
end run

on replace_text(thisText, searchString, replaceString)
	set AppleScript's text item delimiters to searchString
	set textItems to text items of thisText
	set AppleScript's text item delimiters to replaceString
	set thisText to textItems as string
	set AppleScript's text item delimiters to ""
	return thisText
end replace_text

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
