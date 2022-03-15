interesting = {

    'jsc': (['jsc'], '2022-01-21T17:24:29+00:00', [
        """PDF document, version 1.4PDF document, version 1.6PDF document, version 1.1PDF document, version 1.0PDF document, version 1.5PDF document, version 1.1, ASCII textISO-8859 textPDF document, version 1.2PDF document, version 1.7PDF document, version 1.3""",
    ]),

    'libexif': (['exif_loader_fuzzer'], '2020-12-10T09:49:27+11:00', [
        """JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, Exif Standard: [TIFF image data, big-endian, direntries=5, orientation=[*5*], xresolution=74, yresolution=82, resolutionunit=2], baseline, precision 8, 450x600, components 3,
        JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, Exif Standard: [TIFF image data, little-endian, direntries=11, manufacturer=Panasonic, model=DMC-FZ30, orientation=upper-left, xresolution=166, yresolution=174, resolutionunit=2, software=GIMP 2.4.5, datetime=2008:07:31 16:39:24], baseline, precision 8, 100x75, components 3,
        JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, Exif Standard: [TIFF image data, little-endian, direntries=11, manufacturer=Canon, model=Canon EOS 40D, orientation=upper-left, xresolution=166, yresolution=174, resolutionunit=2, software=GIMP 2.4.5, datetime=2008:07:31 10:38:11, GPS-Data], baseline, precision 8, 100x68, components 3""",
    ]),

    'ntp': (['ntp'], '2022-01-21T17:24:29+00:00', [
        """PDF document, version 1.4PDF document, version 1.6PDF document, version 1.1PDF document, version 1.0PDF document, version 1.5PDF document, version 1.1, ASCII textISO-8859 textPDF document, version 1.2PDF document, version 1.7PDF document, version 1.3""",
    ]),

    'mupdf': (['pdf_fuzzer'], '2020-07-06T13:18:23-07:00', [
        """PDF document, version 1.1, ASCII textISO-8859 textPDF document, version 1.4PDF document, version 1.5PDF document, version 1.6PDF document, version 1.1PDF document, version 1.0PDF document, version 1.2PDF document, version 1.7PDF document, version 1.3""",
    ]),

    'ghostscript': (['gstoraster_fuzzer'], '2022-01-28T17:47:00+00:00', [
        """PostScript document text conforming DSC level 1.0PDF document, version 1.7PDF document, version 1.6PostScript document text""",
    ]),

    'libpng-proto': (['png_proto_fuzzer_example'], '2022-01-28T17:47:00+00:00', [
        """PDF document, version 1.2PDF document, version 1.1ISO-8859 textPDF document, version 1.4PDF document, version 1.6PDF document, version 1.1, ASCII textPDF document, version 1.0PDF document, version 1.5PDF document, version 1.7PDF document, version 1.3""",
    ]),

    'nodejs': (['fuzz_url'], '2021-11-22T20:30:59+00:00', [
        """PDF document, version 1.2-1.7"""
    ]),
}

"""
'opencv': ('core_fuzzer', '2021-11-22T20:30:59+00:00')
['8e7afb09a27baa192b083165d540c82dde202a39: Zip archive data, at least v1.0 to extract\n']
['afa09cafdb9d75f794aef46ad58014fcc8bea7e6: XZ compressed data\n'] 
['a47c670bed79278c6be510b67572623bb72d00c2: gzip compressed data, last modified: Sat Aug 11 22:19:30 2018, max compression, from Unix, original size modulo 2^32 10240\n']


'jbig2dec': ('jbig2_fuzzer', '2021-11-22T20:30:59+00:00')
['1f143e95bf57d8d2696525797e198efd785f7221: PGP Secret Sub-key -\n'] 


'libevent': ('parse_query_fuzzer', '2021-11-22T20:30:59+00:00')
['1d529527785345ec49f4f6941a87dc004c7815a4: PDF document, version 1.7\n'] 

'kimageformats': ('kimgio_fuzzer', '2021-11-22T20:30:59+00:00')
['db9c5868dde7fbe2588bd0f1be24bc1d209c3848: Zip archive data, at least v6.3 to extract\n'] 
['a4fe4a45e34fed11d9d8eb9b41a9130e527b2d2a: Zip archive data, at least v1.0 to extract\n'] 
['6e099c52c2c1ed597fa6a65c2c434d3f4532befa: XZ compressed data\n'] 
['5e127a8eb43b93be129431785fc414bf901e1c72: XZ compressed data\n'] 
['3436bf5677ff40b8994835f69749fc41709dab8d: Zip archive data, at least v1.0 to extract\n'] 

'tailscale': ('tailscale', '2022-01-12T22:34:11+00:00')
b6d5cec884ad05e701313f1be41510b3a7c29562: PostScript document text
5eb368ec30c2952742fa67eaf26e36b0b75a7598: PDF document, version 1.6
e0d883600058eaa99c5d76c91a56f2bd497990a8: PDF document, version 1.7
9e14f3978701ac8d95161596fe066f46b76db55e: PostScript document text conforming DSC level 1.0

'jbig2dec': ('jbig2_fuzzer', '2022-01-28T17:47:00+00:00', [
'PGP Secret Sub-key -'
]),


'karchive': ('karchive_fuzzer', '2022-01-28T17:47:00+00:00', [
'gzip compressed data, was "foo", last modified: Sat Jun 18 11:23:13 2016, from Unix, original size modulo 2^32 4'
'data'
'XZ compressed data'
'Zip archive data (empty)'
'gzip compressed data, last modified: Mon Mar 19 14:13:14 2007, from Unix, original size modulo 2^32 133120'

'libexif': ('exif_from_data_fuzzer', exif_loader_fuzzer, '2022-01-28T17:47:00+00:00', [
'JPEG image data, Exif standard: [TIFF image data, little-endian, direntries=9, manufacturer=Canon, model=Canon PowerShot S70, orientation=upper-right, xresolution=148, yresolution=156, resolutionunit=2, datetime=2009:10:10 16:42:32]'
'JPEG image data, Exif standard: [TIFF image data, little-endian, direntries=12, description=                               , manufacturer=NIKON, model=COOLPIX P6000, orientation=upper-left, xresolution=210, yresolution=218, resolutionunit=2, software=Nikon Transfer 1.1 W, datetime=2008:11:01 21:15:09, GPS-Data], baseline, precision 8, 640x480, components 3'
'JPEG image data, Exif standard: [TIFF image data, little-endian, direntries=11, manufacturer=FUJIFILM, model=MX-1700ZOOM, 

'libpng-proto': ('png_proto_fuzzer_example', '2022-01-28T17:47:00+00:00', [
'PDF document, version 1.2'
'PDF document, version 1.1'
'ISO-8859 text'
'PDF document, version 1.4'
'PDF document, version 1.6'
'PDF document, version 1.1, ASCII text'
'PDF document, version 1.0'
'PDF document, version 1.5'
'PDF document, version 1.7'
'PDF document, version 1.3'
]),
"""
