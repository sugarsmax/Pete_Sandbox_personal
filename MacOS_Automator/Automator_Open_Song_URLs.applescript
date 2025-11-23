

on run {input, parameters}
	-- Get the current track URL from Spotify
	tell application "Spotify"
		set currentTrackURL to spotify url of current track
		set name_ to name of current track
		set artist_ to artist of current track
	end tell
	

	-- Create hyphen versions for WhoSampled (convert spaces to hyphens)
	set AppleScript's text item delimiters to " "
	set artist_hyphen to (text items of artist_) as string
	set AppleScript's text item delimiters to "-"
	set artist_hyphen to artist_hyphen as string

	set AppleScript's text item delimiters to " "
	set name_hyphen to (text items of name_) as string
	set AppleScript's text item delimiters to "-"
	set name_hyphen to name_hyphen as string
	

	-- Extract the track ID from the Spotify URL
	set trackID to text 15 thru -1 of currentTrackURL
	
	-- Construct URLs 
	set spotify_URL to "https://open.spotify.com/search/" & name_
	
	set lastfm_my_top to "https://www.last.fm/user/sugarsmax/library/music/" & artist_ & "/+tracks"
--	https://www.last.fm/user/sugarsmax/library/music/BALTHVS/+tracks


	set lastfm_all_top to "https://www.last.fm/music/" & artist_ & "/+tracks?date_preset=ALL#top-tracks"
-- https://www.last.fm/music/BALTHVS/+tracks?date_preset=ALL#top-tracks

	set youtube_url to "https://www.youtube.com/results?search_query=" & artist_ & " " & name_
	
	set whosampled_url to "https://www.whosampled.com/" & artist_hyphen & "/" & name_hyphen

	-- Display the track name and URL in a dialog box for verification
	display dialog "Artist: " & artist_ & return & "Name: " & name_hyphen
	
	tell application "Safari"
		activate
		open location spotify_URL
		open location lastfm_my_top
		open location lastfm_all_top
		open location youtube_url
        open location whosampled_url
	end tell
	
	return input
end run


