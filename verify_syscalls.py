import re

path = "hw3.c.txt"

f = open(path, 'r');
rc_var_name = "";
user_funcs = set(["exit", "strerror", "printf", "close", "closedir", "sizeof", "free", "pthread_exit", "srand", "time", "rand", "sleep"]) # not really user-defined functions, but we don't need to check their return value
line_count = 0

for line in f:
	line_count += 1
	# ignore lines which are commented out (TODO: currently supporting only "//", not "/* ... */")
	if (line.strip().startswith("//")):
		continue

	# in case the previous line has assigned the return value of a non-user-defined function into a variable, then make sure we actually check its value
	if (rc_var_name != ""): 
		if (not re.match("^if[ ]?\([ ]?" + rc_var_name, line.strip())): #line.strip().startswith("if("+rc_var_name)):
			print "error in line #", line_count, ": didn't check the value of variable " + rc_var_name + "(from previous line)"
		# reset the var_name for next line check
		rc_var_name = ""
	# check if the current line defines a user-defined function
	match = re.match("^([a-zA-Z_0-9\*]+) (?P<funcname>[a-zA-Z0-9_]+)\(.*", line)
	if (match):
		user_func_name = match.group("funcname")
		user_funcs.add(user_func_name)
	else:
		#check if the current line calls another function
		match_count = 0
		for match_sub in re.finditer("((?P<assignvar>[a-zA-Z0-9_\-\>\.]+)[ ]?\=[ ]?)?(?P<funcname>[a-zA-Z0-9_]+)\(", line):
			match_count += 1
			#if we have at least one match, then check if it calls a function that isn't user defined
			#TODO: make sure that funcname is not as part of a string which contains a function name for printing only
			if (match_count == 1 and match_sub.group("funcname") not in user_funcs):
				# only the first match can be either with "if" clause or assigned into a variable
				#if so, make sure it's either inside of "if", or that the next line contains "if" (on the result variable)
				if ( (not line.strip().startswith("if")) and match_sub.group("assignvar") ):
					rc_var_name = match_sub.group("assignvar")
				elif (not line.strip().startswith("if")):
					print "error in line #", line_count, ": calling function " + match_sub.group("funcname") + " without checking return value nor assigning into variable for checking in next line"
			else:
				# check on the other matches - for cases when there's more than one function call in one line of code
				# for each of them, make sure we don't call a function that isn't user-defined
				if (match_sub.group("funcname") not in user_funcs):
					print "error in line #", line_count, ": calling function " + match_sub.group("funcname") + " without checking return value"



# NOTES - reference for building/checking the regexs:
# http://www.pyregex.com/
# http://pythex.org/