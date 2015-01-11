## Terminality

A Sublime Text 3 Plugin for Internal Terminal

### What is Terminality
Terminality is a plugin to allows Sublime Text to be used as Terminal. This included input and output from/to Sublime Text's buffer. Although Terminality can run many commands, it **is not gurranteed** that it can be used for all commands.

### How can I created my own command to be used with Terminality?
You can create your own command to be used with Terminality by open Terminality user's setting file and set the settings in following format...

```
{
	... Your other settings ...
	"additional_execution_units": {
		"<Language scope to be used with>": {
			"<Action Name such as Compile or Run>": {
				// All keys in here can be omitted except "command"
				"location": "<String or Macro for location path will be used to run command>",
				"command": "<String or Macro to define command>",
				"read_only": <Boolean indicated whether Terminal is read-only or not>,
				"macro": {<A dictionary contains custom macros (See Macros section belows)>}
			}
		}
	},
	... Your other settings ...
}
```

### Custom Macros
You can create your own macro to be used with custom command by adding each macro to `macro` section in your execution unit (See command format aboves). Each macro is a key-value pairs which key indicated macro name to be used and value is a list of string or pre-defined macros.