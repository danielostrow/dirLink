require 'json'
require 'open-uri'
require 'uri'
require 'pdf-reader'
require 'docx'
require 'csv'
require 'nokogiri'

def extract_links_from_pdf(file_path)
  links = []
  reader = PDF::Reader.new(file_path)
  reader.pages.each do |page|
    page.text.scan(/https?:\/\/[\S]+/) do |url|
      links << url
    end
  end
  links
end

def extract_links_from_docx(file_path)
  links = []
  doc = Docx::Document.open(file_path)
  doc.paragraphs.each do |p|
    p.text.scan(/https?:\/\/[\S]+/) do |url|
      links << url
    end
  end
  links
end

def extract_links_from_csv(file_path)
  links = []
  CSV.foreach(file_path) do |row|
    row.each do |cell|
      cell.scan(/https?:\/\/[\S]+/) do |url|
        links << url
      end
    end
  end
  links
end

def extract_links_from_html(file_path)
  links = []
  html = File.read(file_path)
  doc = Nokogiri::HTML(html)
  doc.css('a').each do |link|
    url = link['href']
    next unless url && !url.empty?
    links << url
  end
  links
end

def extract_links_from_txt(file_path)
  links = []
  text = File.read(file_path)
  text.scan(/https?:\/\/[\S]+/) do |url|
    links << url
  end
  links
end

def extract_links_from_file(file_path)
  links = []
  file_type = File.extname(file_path).downcase

  case file_type
  when ".pdf"
    links = extract_links_from_pdf(file_path)
  when ".docx"
    links = extract_links_from_docx(file_path)
  when ".csv"
    links = extract_links_from_csv(file_path)
  when ".html", ".htm"
    links = extract_links_from_html(file_path)
  when ".txt"
    links = extract_links_from_txt(file_path)
  end

  links
end

def extract_links_from_directory(directory_path)
  links = []
  files_with_errors = []

  Dir.glob("#{directory_path}/**/*") do |file|
    next if File.directory?(file)

    begin
      links += extract_links_from_file(file)
    rescue StandardError => e
      puts "Error processing file #{file}: #{e.message}"
      files_with_errors << file
      next
    end
  end

  puts "The following files could not be processed: #{files_with_errors.join(', ')}" if files_with_errors.any?
  links
end


def normalize_links(links)
  normalized_links = []
  links.each do |link|
    begin
      normalized_link = URI.decode_www_form_component(URI(link.strip).to_s)
      normalized_links << normalized_link if URI.parse(normalized_link).scheme
    rescue URI::InvalidURIError
      next
    end
  end
  normalized_links.uniq
end

# MAIN -- 
def main(directory_path, output_path)
  links = extract_links_from_directory(directory_path)
  normalized_links = normalize_links(links)
  output = { links: normalized_links }.to_json
  File.write(output_path, output) # write output to file
end

# execution helper
if ARGV.empty? || ARGV.size < 2
puts "Usage: ruby link_extractor.rb directory_path output_file_path"
exit
end

directory_path = ARGV[0]
output_file_path = ARGV[1]
main(directory_path, output_file_path)
