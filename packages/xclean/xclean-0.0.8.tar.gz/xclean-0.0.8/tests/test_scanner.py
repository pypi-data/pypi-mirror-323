import io
import os

import pytest

from xclean.scanner import Scanner


class TestCase:

    @pytest.fixture
    def scanner(self):
        scanner = Scanner(db_path=':memory:')
        return scanner

    @pytest.fixture
    def scanner_with_prompt(self):
        scanner = Scanner(db_path=':memory:', prompt=True)
        return scanner

    @pytest.fixture
    def file_name_1(self):
        return 'file1.jpg'

    @pytest.fixture
    def file_name_2(self):
        return 'file2.jpg'

    @pytest.fixture
    def file_name_3(self):
        return 'file3.png'

    @pytest.fixture
    def file_name_4(self):
        return 'file4.png'

    @pytest.fixture
    def file_name_5(self):
        return 'file5'

    @pytest.fixture(autouse=True)
    def clean_temporary_files(self, scanner, file_name_1, file_name_2):
        trash_dir_path = scanner.trash_directory()
        if trash_dir_path is not None:
            for file_name in (file_name_1, file_name_2):
                file_path = os.path.join(trash_dir_path, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)

    @pytest.fixture
    def master_dir_path(self, tmp_path):
        master_dir_path = os.path.join(tmp_path, 'master')
        if not os.path.exists(master_dir_path):
            os.mkdir(master_dir_path)
        return master_dir_path

    @pytest.fixture
    def duplicate_dir_path(self, tmp_path):
        duplicate_dir_path = os.path.join(tmp_path, 'duplicate')
        if not os.path.exists(duplicate_dir_path):
            os.mkdir(duplicate_dir_path)
        return duplicate_dir_path

    @pytest.fixture
    def duplicate_sub_dir_path(self, duplicate_dir_path):
        sub_dir_path = os.path.join(duplicate_dir_path, 'subdir')
        if not os.path.exists(sub_dir_path):
            os.mkdir(sub_dir_path)
        return sub_dir_path

    @pytest.fixture
    def archive_dir_path(self, tmp_path):
        archive_dir_path = os.path.join(tmp_path, 'archive')
        if not os.path.exists(archive_dir_path):
            os.mkdir(archive_dir_path)
        return archive_dir_path

    @pytest.fixture
    def newfiles_dir_path(self, tmp_path):
        archive_dir_path = os.path.join(tmp_path, 'newfiles')
        if not os.path.exists(archive_dir_path):
            os.mkdir(archive_dir_path)
        return archive_dir_path

    @pytest.fixture
    def newfiles_sub_dir_path(self, newfiles_dir_path):
        archive_dir_path = os.path.join(newfiles_dir_path, 'subdir')
        if not os.path.exists(archive_dir_path):
            os.mkdir(archive_dir_path)
        return archive_dir_path

    @pytest.fixture
    def db_file(self, tmp_path):
        db_file = os.path.join(tmp_path, 'db.sqlite3')
        return db_file

    @pytest.fixture
    def m_file1(self, master_dir_path, file_name_1):
        m_file1 = os.path.join(master_dir_path, file_name_1)
        with open(m_file1, 'w') as fp:
            fp.write('a'*1500)
        return m_file1

    @pytest.fixture
    def m_file1_xmp1(self, master_dir_path, file_name_1):
        m_file1 = os.path.join(master_dir_path, f'{file_name_1}.xmp')
        with open(m_file1, 'w') as fp:
            fp.write('a'*150)
        return m_file1

    @pytest.fixture
    def m_file1_xmp2(self, master_dir_path, file_name_1):
        m_file1 = os.path.join(master_dir_path, f'{file_name_1}.XMP')
        with open(m_file1, 'w') as fp:
            fp.write('a'*150)
        return m_file1

    @pytest.fixture
    def m_file1_xmp3(self, master_dir_path, file_name_1):
        prefix, extn = os.path.splitext(file_name_1)
        m_file1 = os.path.join(master_dir_path, f'{prefix}.xmp')
        with open(m_file1, 'w') as fp:
            fp.write('a'*150)
        return m_file1

    @pytest.fixture
    def m_file1_xmp4(self, master_dir_path, file_name_1):
        prefix, extn = os.path.splitext(file_name_1)
        m_file1 = os.path.join(master_dir_path, f'{prefix}.XMP')
        with open(m_file1, 'w') as fp:
            fp.write('a'*150)
        return m_file1

    @pytest.fixture
    def m_file1_link(self, master_dir_path, m_file1):
        m_file1_link = os.path.join(master_dir_path, 'file1.link.txt')
        os.symlink(m_file1, m_file1_link)
        return m_file1_link

    @pytest.fixture
    def m_file2(self, master_dir_path, file_name_2):
        m_file2 = os.path.join(master_dir_path, file_name_2)
        with open(m_file2, 'w') as fp:
            fp.write('b'*1600)
        return m_file2

    @pytest.fixture
    def m_file2_xmp1(self, master_dir_path, file_name_2):
        m_file1 = os.path.join(master_dir_path, f'{file_name_2}.xmp')
        with open(m_file1, 'w') as fp:
            fp.write('a'*160)
        return m_file1

    @pytest.fixture
    def m_file3(self, master_dir_path, file_name_3):
        m_file3 = os.path.join(master_dir_path, file_name_3)
        with open(m_file3, 'w') as fp:
            fp.write('a'*1700)
        return m_file3

    @pytest.fixture
    def m_file4(self, master_dir_path, file_name_4):
        m_file4 = os.path.join(master_dir_path, file_name_4)
        with open(m_file4, 'w') as fp:
            fp.write('b'*1800)
        return m_file4

    @pytest.fixture
    def m_file5(self, master_dir_path, file_name_5):
        m_file5 = os.path.join(master_dir_path, file_name_5)
        with open(m_file5, 'w') as fp:
            fp.write('c'*1900)
        return m_file5

    @pytest.fixture
    def d_file1(self, duplicate_sub_dir_path, file_name_1):
        d_file1 = os.path.join(duplicate_sub_dir_path, file_name_1)
        with open(d_file1, 'w') as fp:
            fp.write('a'*1500)
        return d_file1

    @pytest.fixture
    def d_file1_xmp1(self, duplicate_sub_dir_path, file_name_1):
        d_file1 = os.path.join(duplicate_sub_dir_path, f'{file_name_1}.xmp')
        with open(d_file1, 'w') as fp:
            fp.write('a'*150)
        return d_file1

    @pytest.fixture
    def d_file1_xmp2(self, duplicate_sub_dir_path, file_name_1):
        m_file1 = os.path.join(duplicate_sub_dir_path, f'{file_name_1}.XMP')
        with open(m_file1, 'w') as fp:
            fp.write('a'*150)
        return m_file1

    @pytest.fixture
    def d_file1_xmp3(self, duplicate_sub_dir_path, file_name_1):
        prefix, extn = os.path.splitext(file_name_1)
        m_file1 = os.path.join(duplicate_sub_dir_path, f'{prefix}.xmp')
        with open(m_file1, 'w') as fp:
            fp.write('a'*150)
        return m_file1

    @pytest.fixture
    def d_file1_xmp4(self, duplicate_sub_dir_path, file_name_1):
        prefix, extn = os.path.splitext(file_name_1)
        m_file1 = os.path.join(duplicate_sub_dir_path, f'{prefix}.XMP')
        with open(m_file1, 'w') as fp:
            fp.write('a'*150)
        return m_file1

    @pytest.fixture
    def d_file2(self, duplicate_sub_dir_path, file_name_2):
        d_file2 = os.path.join(duplicate_sub_dir_path, file_name_2)
        with open(d_file2, 'w') as fp:
            fp.write('b'*1600)
        return d_file2

    @pytest.fixture
    def d_file2_xmp1(self, duplicate_sub_dir_path, file_name_2):
        d_file1 = os.path.join(duplicate_sub_dir_path, f'{file_name_2}.xmp')
        with open(d_file1, 'w') as fp:
            fp.write('a'*160)
        return d_file1

    @pytest.fixture
    def d_file3(self, duplicate_sub_dir_path, file_name_3):
        d_file3 = os.path.join(duplicate_sub_dir_path, file_name_3)
        with open(d_file3, 'w') as fp:
            fp.write('a'*1700)
        return d_file3

    @pytest.fixture
    def d_file3_1(self, duplicate_sub_dir_path, file_name_3):
        d_file3 = os.path.join(duplicate_sub_dir_path, file_name_3)
        with open(d_file3, 'w') as fp:
            fp.write('a'*1500)
        return d_file3

    @pytest.fixture
    def d_file3_xmp1(self, duplicate_sub_dir_path, file_name_3):
        d_file1 = os.path.join(duplicate_sub_dir_path, f'{file_name_3}.xmp')
        with open(d_file1, 'w') as fp:
            fp.write('a'*170)
        return d_file1

    @pytest.fixture
    def d_file4(self, duplicate_sub_dir_path, file_name_4):
        d_file4 = os.path.join(duplicate_sub_dir_path, file_name_4)
        with open(d_file4, 'w') as fp:
            fp.write('b'*1800)
        return d_file4

    @pytest.fixture
    def d_file4_2(self, duplicate_sub_dir_path, file_name_4):
        d_file4 = os.path.join(duplicate_sub_dir_path, file_name_4)
        with open(d_file4, 'w') as fp:
            fp.write('b'*1600)
        return d_file4

    @pytest.fixture
    def d_file4_xmp1(self, duplicate_sub_dir_path, file_name_4):
        d_file1 = os.path.join(duplicate_sub_dir_path, f'{file_name_4}.xmp')
        with open(d_file1, 'w') as fp:
            fp.write('a'*180)
        return d_file1

    def test_clean_database_not_needed(
            self,
            db_file
    ):
        if os.path.exists(db_file):
            os.remove(db_file)
        Scanner(db_path=db_file, clean=True)
        stats = os.stat(db_file)
        assert stats.st_size != 100

    def test_clean_database(
            self,
            db_file
    ):
        with open(db_file, 'w') as fp:
            fp.write('a'*100)
        Scanner(db_path=db_file, clean=True)
        stats = os.stat(db_file)
        assert stats.st_size != 100

    def test_scan_master(
            self,
            scanner,
            master_dir_path,
            m_file1, m_file2
    ):
        results = scanner.scan(dir_path=str(master_dir_path))
        assert results == {
            'files': {
                'count': 2,
                'size': 3100,
            }
        }
        assert len(os.listdir(master_dir_path)) == 2

    def test_scan_master_with_extension(
            self,
            scanner,
            master_dir_path,
            m_file1, m_file4
    ):
        results = scanner.scan(dir_path=str(master_dir_path), include=['jpg'])
        assert results == {
            'files': {
                'count': 1,
                'size': 1500,
            }
        }
        assert len(os.listdir(master_dir_path)) == 2

    def test_scan_master_exclude_extension(
            self,
            scanner,
            master_dir_path,
            m_file1, m_file4
    ):
        results = scanner.scan(dir_path=str(master_dir_path), exclude=['jpg'])
        assert results == {
            'files': {
                'count': 1,
                'size': 1800,
            }
        }
        assert len(os.listdir(master_dir_path)) == 2

    def test_scan_master_ignore_link(
            self,
            scanner,
            master_dir_path,
            m_file1, m_file1_link
    ):
        results = scanner.scan(dir_path=str(master_dir_path), include=['jpg'])
        assert results == {
            'files': {
                'count': 1,
                'size': 1500,
            }
        }
        assert len(os.listdir(master_dir_path)) == 2

    def test_scan_master_no_match(
            self,
            scanner,
            master_dir_path,
            m_file3, m_file4
    ):
        results = scanner.scan(dir_path=str(master_dir_path), include=['txt'])
        assert results == {
            'files': {
                'count': 0,
                'size': 0,
            }
        }
        assert len(os.listdir(master_dir_path)) == 2

    def test_scan_master_no_file_extension(
            self,
            scanner,
            master_dir_path,
            m_file5
    ):
        results = scanner.scan(dir_path=str(master_dir_path), include=['txt'])
        assert results == {
            'files': {
                'count': 0,
                'size': 0,
            }
        }
        assert len(os.listdir(master_dir_path)) == 1

    def test_clean_match(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, duplicate_sub_dir_path,
            m_file1, m_file2, d_file3_1, d_file4_2
    ):
        scanner.scan(dir_path=str(master_dir_path))
        results = scanner.clean(dir_path=str(duplicate_dir_path))
        assert results == {
            'duplicates': {
                'count': 2,
                'size': 3100,
            },
            'files': {
                'count': 2,
                'size': 3100,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(duplicate_dir_path)) == 1
        assert len(os.listdir(duplicate_sub_dir_path)) == 2

    def test_clean_extension(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, duplicate_sub_dir_path,
            m_file1, m_file2, d_file1, d_file4,
    ):
        scanner.scan(dir_path=str(master_dir_path))
        results = scanner.clean(dir_path=str(duplicate_dir_path), include=['jpg'])
        assert results == {
            'duplicates': {
                'count': 1,
                'size': 1500,
            },
            'files': {
                'count': 1,
                'size': 1500,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(duplicate_dir_path)) == 1
        assert len(os.listdir(duplicate_sub_dir_path)) == 2

    def test_clean_no_dups(
            self, scanner,
            master_dir_path, duplicate_dir_path, duplicate_sub_dir_path,
            m_file1, m_file2, d_file3, d_file4,
    ):
        results = scanner.clean(dir_path=str(duplicate_dir_path))
        assert results == {
            'duplicates': {
                'count': 0,
                'size': 0,
            },
            'files': {
                'count': 2,
                'size': 3500,
            },
            'new': {
                'count': 2,
                'size': 3500,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(duplicate_dir_path)) == 1
        assert len(os.listdir(duplicate_sub_dir_path)) == 2

    def test_clean_archive_newfiles(
            self,
            scanner, master_dir_path, duplicate_dir_path, newfiles_dir_path, newfiles_sub_dir_path,
            m_file1, m_file1_xmp1, m_file2, m_file2_xmp1,
            d_file3, d_file3_xmp1, d_file4, d_file4_xmp1,
    ):
        results = scanner.clean(
            dir_path=str(duplicate_dir_path),
            archive_new=str(newfiles_dir_path),
        )
        assert results == {
            'duplicates': {
                'count': 0,
                'size': 0,
            },
            'files': {
                'count': 4,
                'size': 3500,
            },
            'new': {
                'count': 2,
                'size': 3500,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 4
        assert len(os.listdir(duplicate_dir_path)) == 0
        assert len(os.listdir(newfiles_dir_path)) == 1
        assert len(os.listdir(newfiles_sub_dir_path)) == 4

    def test_clean_archive_newfiles_prompt(
            self,
            scanner_with_prompt,
            master_dir_path, duplicate_dir_path, newfiles_dir_path, newfiles_sub_dir_path,
            m_file1, m_file1_xmp1, m_file2, m_file2_xmp1,
            d_file3, d_file3_xmp1, d_file4, d_file4_xmp1,
            monkeypatch,
    ):
        monkeypatch.setattr('sys.stdin', io.StringIO('y\n y\n y\n y\n'))
        results = scanner_with_prompt.clean(
            dir_path=str(duplicate_dir_path),
            archive_new=str(newfiles_dir_path),
        )
        assert results == {
            'duplicates': {
                'count': 0,
                'size': 0,
            },
            'files': {
                'count': 4,
                'size': 3500,
            },
            'new': {
                'count': 2,
                'size': 3500,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 4
        assert len(os.listdir(duplicate_dir_path)) == 0
        assert len(os.listdir(newfiles_dir_path)) == 1
        assert len(os.listdir(newfiles_sub_dir_path)) == 4

    def test_clean_no_match(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, duplicate_sub_dir_path,
            m_file1, m_file2, d_file3, d_file4,
    ):
        results = scanner.clean(dir_path=str(duplicate_dir_path), include=['txt'])
        assert results == {
            'duplicates': {
                'count': 0,
                'size': 0,
            },
            'files': {
                'count': 0,
                'size': 0,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(duplicate_dir_path)) == 1
        assert len(os.listdir(duplicate_sub_dir_path)) == 2

    def test_clean_masters_does_nothing(
            self,
            scanner,
            master_dir_path,
            m_file1, m_file2, m_file3, m_file4
    ):
        scanner.scan(dir_path=str(master_dir_path))
        results = scanner.clean(dir_path=str(master_dir_path))
        assert results == {
            'duplicates': {
                'count': 0,
                'size': 0,
            },
            'files': {
                'count': 0,
                'size': 0,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 4

    def test_archive_duplicates(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1
    ):
        scanner.scan(dir_path=master_dir_path)
        results = scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path)
        assert results == {
            'duplicates': {
                'count': 1,
                'size': 1500,
            },
            'files': {
                'count': 1,
                'size': 1500,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(archive_dir_path)) == 1

    def test_archive_multiple_duplicates(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file2, d_file1, d_file2
    ):
        scanner.scan(dir_path=master_dir_path)
        results = scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path)
        assert results == {
            'duplicates': {
                'count': 2,
                'size': 3100,
            },
            'files': {
                'count': 2,
                'size': 3100,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(archive_dir_path)) == 1
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_remove_duplicates(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1, file_name_1
    ):
        scanner.scan(dir_path=master_dir_path)
        results = scanner.clean(dir_path=duplicate_dir_path, remove_dups=True)
        assert results == {
            'duplicates': {
                'count': 1,
                'size': 1500,
            },
            'files': {
                'count': 1,
                'size': 1500,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(archive_dir_path)) == 0
        if scanner.trash_directory() is not None:
            assert not os.path.exists(os.path.join(scanner.trash_directory(), file_name_1))

    def test_trash_duplicates(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1, file_name_1
    ):
        scanner.scan(dir_path=master_dir_path)
        results = scanner.clean(dir_path=duplicate_dir_path, trash_dups=True)
        assert results == {
            'duplicates': {
                'count': 1,
                'size': 1500,
            },
            'files': {
                'count': 1,
                'size': 1500,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': False,
        }
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(archive_dir_path)) == 0
        if scanner.trash_directory() is not None:
            assert os.path.exists(os.path.join(scanner.trash_directory(), file_name_1))

    def test_no_trash_directory(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1, file_name_1
    ):
        scanner.trash_directory = lambda : None
        scanner.scan(dir_path=master_dir_path)
        results = scanner.clean(dir_path=duplicate_dir_path, trash_dups=True)
        assert results == {
            'duplicates': {
                'count': 1,
                'size': 1500,
            },
            'files': {
                'count': 1,
                'size': 1500,
            },
            'new': {
                'count': 0,
                'size': 0,
            },
            'abort': True,
        }
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 1
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_no_xmps(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(archive_dir_path)) == 1

    def test_xmp_compare_no_dup_xmp1(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp1, d_file1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 1
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_no_dup_xmp2(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp2, d_file1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 1
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_no_dup_xmp3(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp3, d_file1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 1
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_no_dup_xmp4(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp4, d_file1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 1
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_xmp1_dup_only(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1, d_file1_xmp1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 2
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_xmp2_dup_only(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1, d_file1_xmp2
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 2
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_xmp3_dup_only(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1, d_file1_xmp3
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 2
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_xmp4_dup_only(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, d_file1, d_file1_xmp4
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True)
        assert len(os.listdir(master_dir_path)) == 1
        assert len(os.listdir(os.path.dirname(d_file1))) == 2
        assert len(os.listdir(archive_dir_path)) == 0

    def test_xmp_compare_xmp1_xmp1(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp1, d_file1, d_file1_xmp1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp2_xmp1(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp2, d_file1, d_file1_xmp1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp3_xmp1(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp3, d_file1, d_file1_xmp1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp4_xmp1(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp4, d_file1, d_file1_xmp1
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp1_xmp2(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp1, d_file1, d_file1_xmp2
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp2_xmp2(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp2, d_file1, d_file1_xmp2
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp3_xmp2(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp3, d_file1, d_file1_xmp2
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp4_xmp2(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp4, d_file1, d_file1_xmp2
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp1_xmp3(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp1, d_file1, d_file1_xmp3
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp2_xmp3(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp2, d_file1, d_file1_xmp3
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp3_xmp3(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp3, d_file1, d_file1_xmp3
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp4_xmp3(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp4, d_file1, d_file1_xmp3
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp1_xmp4(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp1, d_file1, d_file1_xmp4
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp2_xmp4(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp2, d_file1, d_file1_xmp4
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp3_xmp4(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp3, d_file1, d_file1_xmp4
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2

    def test_xmp_compare_xmp4_xmp4(
            self,
            scanner,
            master_dir_path, duplicate_dir_path, archive_dir_path,
            m_file1, m_file1_xmp4, d_file1, d_file1_xmp4
    ):
        scanner.scan(dir_path=master_dir_path)
        scanner.clean(dir_path=duplicate_dir_path, archive_to=archive_dir_path, check_xmp=True, include=['jpg'])
        assert len(os.listdir(master_dir_path)) == 2
        assert len(os.listdir(os.path.dirname(d_file1))) == 0
        assert len(os.listdir(os.path.join(archive_dir_path, 'subdir'))) == 2
