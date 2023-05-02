# dirLink
Tool is used to extract all links within a given directory.
Outputs to JSON

Requirements:
```
require 'json'
require 'open-uri'
require 'uri'
require 'pdf-reader'
require 'docx'
require 'csv'
require 'nokogiri'
```
These requirements below are not default with Ruby. Install.
```
gem install pdf-reader
gem install docx
gem install nokogiri
```

Current Supported File Types:
- docx
- pdf only if file structure is stable
- html
- csv
- txt

- Adding more

