## Terminality Development Plan

To do:

- Travis supported
- More complex macro system (at least for java compile and run)

### Complex Macro System

- Substring `$file_name[1:]`
- RegEx captures

If each element is...

- String => Plain Dynamic Macro
- Patterned String => Substring
- List of String, Integer => RegEx with Capture
- List of String, String, Integer => Dynamic Macro with RegEx
- List of String, Patterned String => Dynamic Macro with Substring

Use `^(-?\d+)?:(-?\d+)?$` to validate substring pattern

```
"macros": {
	"file_name_without_ext": [
		"$filename", //Dynamic Macro
		"-1:", //Substring
		[".*(?=\\.)"], //RegEx
		["$filename", ".*(?=\\.)"], //Dynamic Macro with RegEx
		["$filename", "-1:"], //Dynamic Macro with Substring
	]
}
```