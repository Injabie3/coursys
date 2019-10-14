# Generated by Django 2.0.13 on 2019-06-01 16:52

from django.db import migrations, models
import django.db.models.deletion
import submission.models.base


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0005_on_delete'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveCodeComponent',
            fields=[
                ('submissioncomponent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='submission.SubmissionComponent')),
                ('language', models.CharField(choices=[('apl', 'APL'), ('asn.1', 'ASN.1'), ('clojure', 'Clojure'), ('cmake', 'CMake'), ('cobol', 'COBOL'), ('coffeescript', 'CoffeeScript'), ('commonlisp', 'Common Lisp'), ('crystal', 'Crystal'), ('css', 'CSS'), ('cypher', 'Cypher'), ('d', 'D'), ('dart', 'Dart'), ('diff', 'diff'), ('django', 'Django template'), ('dockerfile', 'Dockerfile'), ('dtd', 'DTD'), ('dylan', 'Dylan'), ('ebnf', 'EBNF'), ('ecl', 'ECL'), ('eiffel', 'Eiffel'), ('elm', 'Elm'), ('erlang', 'Erlang'), ('factor', 'Factor'), ('fcl', 'FCL'), ('forth', 'Forth'), ('fortran', 'Fortran'), ('gas', 'Gas'), ('gherkin', 'Gherkin'), ('go', 'Go'), ('groovy', 'Groovy'), ('haml', 'HAML'), ('handlebars', 'Handlebars'), ('haskell', 'Haskell'), ('haskell-literate', 'Haskell, Literate'), ('haxe', 'Haxe'), ('http', 'HTTP'), ('idl', 'IDL'), ('javascript', 'JavaScript'), ('jinja2', 'Jinja2'), ('jsx', 'JSX'), ('julia', 'Julia'), ('livescript', 'LiveScript'), ('lua', 'Lua'), ('markdown', 'Markdown'), ('gfm', 'Markdown, GitHub-flavour'), ('mathematica', 'Mathematica'), ('modelica', 'Modelica'), ('ntriples', 'N-Triples/N-Quads'), ('nginx', 'Nginx'), ('nsis', 'NSIS'), ('mllike', 'OCaml'), ('octave', 'Octave'), ('oz', 'Oz'), ('pascal', 'Pascal'), ('pegjs', 'PEG.js'), ('perl', 'Perl'), ('php', 'PHP'), ('pig', 'Pig Latin'), ('plain-text', 'Plain text (no syntax highlighting)'), ('powershell', 'PowerShell'), ('protobuf', 'ProtoBuf'), ('pug', 'Pug'), ('puppet', 'Puppet'), ('python', 'Python'), ('q', 'Q'), ('r', 'R'), ('rst', 'reStructuredText'), ('rpm', 'RPM'), ('ruby', 'Ruby'), ('rust', 'Rust'), ('sas', 'SAS'), ('sass', 'Sass'), ('scheme', 'Scheme'), ('shell', 'Shell'), ('sieve', 'Sieve'), ('slim', 'Slim'), ('smalltalk', 'Smalltalk'), ('smarty', 'Smarty'), ('solr', 'Solr'), ('soy', 'Soy'), ('sparql', 'SPARQL'), ('sql', 'SQL'), ('clike', 'Squirrel'), ('stex', 'sTeX, LaTeX'), ('stylus', 'Stylus'), ('swift', 'Swift'), ('tcl', 'Tcl'), ('textile', 'Textile'), ('tiddlywiki', 'Tiddlywiki'), ('tiki', 'Tiki wiki'), ('toml', 'TOML'), ('tornado', 'Tornado template'), ('troff', 'troff'), ('turtle', 'Turtle'), ('twig', 'Twig'), ('vb', 'VB.NET'), ('vbscript', 'VBScript'), ('velocity', 'Velocity'), ('verilog', 'Verilog/SystemVerilog'), ('vhdl', 'VHDL'), ('vue', 'Vue.js app'), ('webidl', 'Web IDL'), ('xml', 'XML/HTML'), ('xquery', 'XQuery'), ('yacas', 'Yacas'), ('yaml', 'YAML'), ('z80', 'Z80')], help_text='Programming language being submitted (will be used for syntax highlighting in entry box.', max_length=50, verbose_name='Programming Language')),
                ('file_ext', models.CharField(help_text='File extension you want when downloading the results (like “py” for Python code).', max_length=10, verbose_name='File Extension')),
                ('max_size', submission.models.base.FileSizeField(default=10, help_text='Maximum length, in kB.')),
            ],
            bases=('submission.submissioncomponent',),
        ),
        migrations.CreateModel(
            name='SubmittedLiveCode',
            fields=[
                ('submittedcomponent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='submission.SubmittedComponent')),
                ('text', models.TextField(max_length=102400, verbose_name='Code')),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='submission.LiveCodeComponent')),
            ],
            bases=('submission.submittedcomponent',),
        ),
    ]