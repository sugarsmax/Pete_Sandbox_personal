on run {input, parameters}
	try
		-- Use shell command to find Tidal process
		set result to do shell script "ps aux | grep -i tidal | grep -v grep"
		display dialog "Found Tidal process:" & return & return & result buttons {"OK"}
		return result
	on error err
		display dialog "Error or Tidal not running:" & return & err buttons {"OK"}
		return err
	end try
end run
