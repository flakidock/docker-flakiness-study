import unittest
from utils.file_utils import read_file
from utils.string_utils import parse_unique_error_files

error_segment = """
> [build 14/27] RUN cd R-4.2.2 &&                                                     . FLAGS &&                                                               CXXFLAGS=-D__MUSL__  ./configure                                             --with-recommended-packages=no                                           --with-readline=yes --with-x=no --enable-java=no                         --enable-R-shlib                                                         --disable-openmp --with-internal-tzcode:
checking whether wctrans exists and is declared... yes
checking whether wctype exists and is declared... yes
checking whether iswctype exists and is declared... yes
checking whether wcwidth exists and is declared... yes
checking whether wcswidth exists and is declared... yes
checking for wctrans_t... yes
checking for mbstate_t... yes
configure: error: libcurl >= 7.28.0 library and headers are required with support for https
ERROR: process "/bin/sh -c cd R-${R_VERSION} &&                                                     . FLAGS &&                                                               CXXFLAGS=-D__MUSL__  ./configure                                             --with-recommended-packages=no                                           --with-readline=yes --with-x=no --enable-java=no                         --enable-R-shlib                                                         --disable-openmp --with-internal-tzcode" did not complete successfully: exit code: 1
""".strip()

error_line = """
RUN cd R-${R_VERSION} &&                                                 \\
    . FLAGS &&                                                           \\
    CXXFLAGS=-D__MUSL__  ./configure                                     \\
        --with-recommended-packages=no                                   \\
        --with-readline=yes --with-x=no --enable-java=no                 \\
        --enable-R-shlib                                                 \\
        --disable-openmp --with-internal-tzcode
""".strip()

class TestParseUniqueEerrorFiles(unittest.TestCase):
    def test_get_error_segments_as_json(self):
        path = 'test-docker-error-parser/unique-build-error-log.log'
        raw_build_log = read_file(path)
        docker_error_trace = parse_unique_error_files(raw_build_log)

        self.assertEqual(docker_error_trace.error_segment, error_segment)
        self.assertEqual(docker_error_trace.error_line, error_line)


if __name__ == '__main__':
    unittest.main()
