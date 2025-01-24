from unittest import TestCase
from six.moves import builtins
from six import assertRaisesRegex, PY3, StringIO
from seqgen.sequences import Sequences
from dark.aaVars import AA_LETTERS

try:
    from unittest.mock import mock_open, patch
except ImportError:
    from mock import mock_open, patch

open_ = ("builtins" if PY3 else "__builtin__") + ".open"


class TestSequences(TestCase):
    """
    Test the Sequences class.
    """

    @patch(open_, new_callable=mock_open)
    def testNonExistentSpecificationFile(self, mock):
        """
        Passing a specification filename that does not exist must raise a
        FileNotFoundError (PY3) or IOError (PY2).
        """
        errorClass = builtins.FileNotFoundError if PY3 else IOError
        mock.side_effect = errorClass("abc")
        error = "^abc$"
        assertRaisesRegex(self, errorClass, error, Sequences, spec="filename")

    @patch(open_, new_callable=mock_open, read_data="not JSON")
    def testNotJSON(self, mock):
        """
        If the specification is not valid JSON, a ValueError must be raised.
        """
        if PY3:
            error = "^Expecting value: line 1 column 1 \\(char 0\\)$"
        else:
            error = "^No JSON object could be decoded$"
        assertRaisesRegex(self, ValueError, error, Sequences, spec="filename")

    @patch(open_, new_callable=mock_open, read_data='{"xxx": 33}')
    def testNoSequencesKey(self, mock):
        """
        If the JSON specification has no 'sequences' key, a ValueError
        must be raised.
        """
        error = "^The specification JSON must have a 'sequences' key\\.$"
        assertRaisesRegex(self, ValueError, error, Sequences, spec="filename")

    @patch(open_, new_callable=mock_open, read_data='[{"id": "a"}, {"id": "a"}]')
    def testDuplicatedId(self, mock):
        """
        If a duplicate sequence id is present in the JSON, a ValueError
        must be raised.
        """
        error = (
            "^Sequence specification 2 has an id \\(a\\) that has "
            "already been used\\.$"
        )
        assertRaisesRegex(self, ValueError, error, Sequences, spec="filename")

    def testNoSequences(self):
        """
        If no sequences are specified, none should be returned.
        """
        s = Sequences(StringIO("[]"))
        self.assertEqual([], list(s))

    def testOneSequenceIdOnly(self):
        """
        If only one sequence is specified, and only by id, one sequence
        should be created, it should have the default length, the expected
        id, and it should be entirely composed of nucleotides.
        """
        s = Sequences(StringIO('[{"id": "the-id"}]'))
        (read,) = list(s)
        self.assertEqual("the-id", read.id)
        self.assertEqual(Sequences.DEFAULT_LENGTH, len(read.sequence))
        self.assertEqual(set(), set(read.sequence) - set("ACGT"))

    def testOneSequenceSequenceOnly(self):
        """
        If only one sequence is specified, and only by its sequence, one
        sequence should be created, and it should have the specified sequence.
        """
        s = Sequences(StringIO('[{"sequence": "ACCG"}]'))
        (read,) = list(s)
        self.assertEqual("ACCG", read.sequence)

    @patch(open_, new_callable=mock_open, read_data=">id1\nACCT\n")
    def testOneSequenceSequenceFileOnly(self, mock):
        """
        If only one sequence is specified, and only by its sequence filename,
        one sequence should be read and created, and it should have the
        specified sequence.
        """
        s = Sequences(StringIO('[{"sequence file": "xxx.fasta"}]'))
        (read,) = list(s)
        self.assertEqual("ACCT", read.sequence)

    @patch(open_, new_callable=mock_open)
    def xxx_testOneSequenceSequenceFileOnlyUnknownFile(self, mock):
        """
        If only one sequence is specified, and only by its sequence filename,
        but the file is unknown, ValueError must be raised.
        """
        s = Sequences(StringIO('[{"sequence file": "xxx.fasta"}]'))
        errorClass = builtins.FileNotFoundError if PY3 else IOError
        mock.side_effect = errorClass("abc")
        error = "^abc$"
        assertRaisesRegex(self, errorClass, error, list, s)

    def testOneSequenceIdAndCountGreaterThanOne(self):
        """
        If only one sequence is specified with an id, a ValueError must be
        raised if its count is greater than one.
        """
        spec = StringIO(
            """{
            "sequences": [
                {
                    "id": "the-id",
                    "count": 6
                }
            ]
        }"""
        )
        error = (
            "^Sequence specification 1 with id 'the-id' has a count of "
            "6\\. If you want to specify a sequence with an id, the "
            "count must be 1\\. To specify multiple sequences with an id "
            "prefix, use 'id prefix'\\.$"
        )
        assertRaisesRegex(self, ValueError, error, Sequences, spec)

    def testRatchetWithNoCount(self):
        """
        If ratchet is specified for seqeunce spec its count must be greater
        than one.
        """
        spec = StringIO(
            """{
            "sequences": [
                {
                    "id": "xxx",
                    "ratchet": true
                }
            ]
        }"""
        )
        error = (
            "^Sequence specification 1 is specified as ratchet but its "
            "count is only 1\\.$"
        )
        assertRaisesRegex(self, ValueError, error, Sequences, spec)

    def testRatchetWithNoMutationRate(self):
        """
        If ratchet is specified for seqeunce spec it must have a mutation
        rate.
        """
        spec = StringIO(
            """{
            "sequences": [
                {
                    "count": 4,
                    "id": "xxx",
                    "ratchet": true
                }
            ]
        }"""
        )
        error = (
            "^Sequence specification 1 is specified as ratchet but does "
            "not give a mutation rate\\.$"
        )
        assertRaisesRegex(self, ValueError, error, Sequences, spec)

    def testUnknownSpecificationKey(self):
        """
        If an unknown key is given in a sequence specification, a ValueError
        must be raised.
        """
        error = "^Sequence specification 1 contains an unknown key: dog\\.$"
        assertRaisesRegex(
            self,
            ValueError,
            error,
            Sequences,
            StringIO(
                """{
            "sequences": [
                {
                    "dog": "xxx"
                }
            ]
        }"""
            ),
        )

    def testUnknownSectionKey(self):
        """
        If an unknown key is given in a sequence specification section, a
        ValueError must be raised.
        """
        for key in "id", "id prefix", "xxx":
            error = (
                "^Section 1 of sequence specification 1 contains an "
                "unknown key: %s\\.$" % key
            )
            assertRaisesRegex(
                self,
                ValueError,
                error,
                Sequences,
                StringIO(
                    """{
                "sequences": [
                    {
                        "sections": [
                            {
                                "%s": "xxx"
                            }
                        ]
                    }
                ]
            }"""
                    % key
                ),
            )

    def testOneLetterAlphabet(self):
        """
        It must be possible to specify an alphabet with just one symbol.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "alphabet": "0"
                }
            ]
        }"""
            ),
            defaultLength=500,
        )
        (read,) = list(s)
        self.assertEqual("0" * 500, read.sequence)

    def testTwoLetterAlphabet(self):
        """
        It must be possible to specify an alphabet with two symbols.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "alphabet": "01"
                }
            ]
        }"""
            ),
            defaultLength=500,
        )
        (read,) = list(s)
        self.assertTrue(x in "01" for x in read.sequence)

    def testOneSequenceIdOnlyDefaultLength(self):
        """
        If only one sequence is specified, and only by id, one sequence
        should be created, and it should have the length passed in
        defaultLength.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "the-id"
                }
            ]
        }"""
            ),
            defaultLength=500,
        )
        (read,) = list(s)
        self.assertEqual("the-id", read.id)
        self.assertEqual(500, len(read.sequence))

    def testOneSequenceIdOnlyDefaultIdPrefix(self):
        """
        If only one sequence is specified, and only by length, one sequence
        should be created, it should have the length passed, and its id taken
        from passed defaultIdPrefix.
        """
        s = Sequences(
            StringIO(
                """{
            "globals": {
                "id prefix": "the-prefix."
            },
            "sequences": [
                {
                    "length": 5
                }
            ]
        }"""
            ),
            defaultIdPrefix="the-prefix.",
        )
        (read,) = list(s)
        self.assertEqual("the-prefix.1", read.id)
        self.assertEqual(5, len(read.sequence))

    def testOneSequenceAAOnly(self):
        """
        If only one sequence is specified, and only by indicating that it
        should be amino acids, one sequence should be created, it should have
        the default length, the expected id, and it should be entirely
        composed of nucleotides.
        """
        s = Sequences(StringIO('[{"random aa": true}]'))
        (read,) = list(s)
        self.assertEqual(Sequences.DEFAULT_ID_PREFIX + "1", read.id)
        self.assertEqual(Sequences.DEFAULT_LENGTH, len(read.sequence))
        self.assertEqual(set(), set(read.sequence) - set(AA_LETTERS))

    def testTwoSequencesSecondFromId(self):
        """
        If only one sequence is given an id and a second refers to it
        by that id, the second sequence should be the same as the first.
        """
        s = Sequences(
            StringIO(
                """[
            {
                "id": "a"
            },
            {
                "from id": "a"
            }
        ]"""
            )
        )
        (read1, read2) = list(s)
        self.assertEqual(read1.sequence, read2.sequence)

    def testTwoSequencesButSecondOneSkipped(self):
        """
        If two sequences are specified but one is skipped, only one
        sequence should result.
        """
        s = Sequences(
            StringIO(
                """[
            {
                "id": "a"
            },
            {
                "id": "b",
                "skip": true
            }
        ]"""
            )
        )
        (read,) = list(s)
        self.assertEqual("a", read.id)

    def testTwoSequencesSecondOneNotSkipped(self):
        """
        If two sequences are specified and skip=false in the second,
        both should be returned.
        """
        s = Sequences(
            StringIO(
                """[
            {
                "id": "a"
            },
            {
                "id": "b",
                "skip": false
            }
        ]"""
            )
        )
        (read1, read2) = list(s)
        self.assertEqual("a", read1.id)
        self.assertEqual("b", read2.id)

    def testOneSequenceByLength(self):
        """
        If only one sequence is specified, and only by giving its length,
        only one sequence should be created, and it should have the given
        length.
        """
        s = Sequences(StringIO('[{"length": 55}]'))
        (read,) = list(s)
        self.assertEqual(55, len(read.sequence))

    def testOneSequenceRandomNTs(self):
        """
        A sequence must be able to be composed of random NTs.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "random nt": true
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual(set(), set(read.sequence) - set("ACGT"))

    def testOneSequenceIdPrefix(self):
        """
        A sequence must be able to be given just using an id prefix.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id prefix": "xxx-"
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual("xxx-1", read.id)

    def testOneSequenceWithIdAndDescription(self):
        """
        A sequence must be able to be given using an id and a description.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "description": "A truly wonderful sequence!",
                    "id": "xxx"
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual("xxx A truly wonderful sequence!", read.id)

    def testTwoSequencesByCount(self):
        """
        If two sequences are requested (only by giving a count) they should
        have the expected lengths and ids.
        """
        s = Sequences(StringIO('[{"count": 2}]'))
        (read1, read2) = list(s)
        self.assertEqual(Sequences.DEFAULT_LENGTH, len(read1.sequence))
        self.assertEqual(Sequences.DEFAULT_ID_PREFIX + "1", read1.id)
        self.assertEqual(Sequences.DEFAULT_LENGTH, len(read2.sequence))
        self.assertEqual(Sequences.DEFAULT_ID_PREFIX + "2", read2.id)

    def testTwoSequencesWithDifferentIdPrefixesAndCounts(self):
        """
        If two sequences are requested with different id prefixes and each
        with a count, the ids must start numbering from 1 for each prefix.
        """
        s = Sequences(
            StringIO(
                """[
            {
                "id prefix": "seq-",
                "count": 2
            },
            {
                "id prefix": "num-",
                "count": 3
            }
        ]"""
            )
        )
        (read1, read2, read3, read4, read5) = list(s)
        self.assertEqual("seq-1", read1.id)
        self.assertEqual("seq-2", read2.id)
        self.assertEqual("num-1", read3.id)
        self.assertEqual("num-2", read4.id)
        self.assertEqual("num-3", read5.id)

    def testOneSequenceLengthIsAVariable(self):
        """
        If only one sequence is specified, and only by giving its length,
        (as a variable) one sequence should be created, and it should have the
        given length.
        """
        s = Sequences(
            StringIO(
                """{
            "variables": {
                "len": 200
            },
            "sequences": [
                {
                    "length": "%(len)d"
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual(200, len(read.sequence))

    def testOneSectionWithLength(self):
        """
        A sequence must be able to be built up from sections, with just one
        section given by length.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "sections": [
                        {
                            "length": 40
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual(40, len(read.sequence))

    def testOneSectionWithSequence(self):
        """
        A sequence must be able to be built up from sections, with just one
        section given by a sequence.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "sections": [
                        {
                            "sequence": "ACTT"
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual("ACTT", read.sequence)

    def testOneSectionRandomNTs(self):
        """
        A sequence must be able to be built up from sections, with just one
        section of random NTs.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "sections": [
                        {
                            "random nt": true
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual(set(), set(read.sequence) - set("ACGT"))

    def testOneSectionRandomAAs(self):
        """
        A sequence must be able to be built up from sections, with just one
        section of random AAs.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "sections": [
                        {
                            "random aa": true
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual(set(), set(read.sequence) - set(AA_LETTERS))

    def testTwoSectionsWithLengths(self):
        """
        A sequence must be able to be built up from sections, with two
        sections given by length.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "sections": [
                        {
                            "length": 40
                        },
                        {
                            "length": 10
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read,) = list(s)
        self.assertEqual(50, len(read.sequence))

    def testSectionWithIdReference(self):
        """
        A sequence must be able to be built up from sections, with two
        sections given by length.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "xxx",
                    "sequence": "ACCGT"
                },
                {
                    "sections": [
                        {
                            "from id": "xxx"
                        },
                        {
                            "length": 10
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read1, read2) = list(s)
        self.assertEqual(15, len(read2.sequence))
        self.assertTrue(read2.sequence.startswith("ACCGT"))

    def testSectionWithUnknownIdReference(self):
        """
        If a sequence is built up from sections and a referred to sequence
        id does not exist, a ValueError must be raised.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "sections": [
                        {
                            "from id": "xxx"
                        }
                    ]
                }
            ]
        }"""
            )
        )
        error = (
            "^Sequence section refers to the id 'xxx' of "
            "non-existent other sequence\\.$"
        )
        assertRaisesRegex(self, ValueError, error, list, s)

    def testSectionWithIdReferenceTooShort(self):
        """
        If a sequence is built up from sections and a referred-to sequence
        is too short for the desired length, a ValueError must be raised.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "xxx",
                    "sequence": "ACCGT"
                },
                {
                    "sections": [
                        {
                            "from id": "xxx",
                            "length": 10
                        }
                    ]
                }
            ]
        }"""
            )
        )
        error = (
            "^Sequence specification refers to sequence id 'xxx', "
            "starting at index 1 with length 10, but sequence 'xxx' is "
            "not long enough to support that\\.$"
        )
        assertRaisesRegex(self, ValueError, error, list, s)

    def testNamedRecombinant(self):
        """
        It must be possible to build up and give an id to a recombinant.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "xxx",
                    "sequence": "ACCA"
                },
                {
                    "id": "yyy",
                    "sequence": "GGTT"
                },
                {
                    "id": "recombinant",
                    "sections": [
                        {
                            "from id": "xxx",
                            "start": 1,
                            "length": 3
                        },
                        {
                            "from id": "yyy",
                            "start": 2,
                            "length": 2
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read1, read2, read3) = list(s)
        self.assertEqual("recombinant", read3.id)
        self.assertEqual("ACCGT", read3.sequence)

    def testRecombinantFromFullOtherSequences(self):
        """
        It must be possible to build up a recombinant that is composed of two
        other sequences by only giving the ids of the other sequences.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "xxx",
                    "sequence": "ACCA"
                },
                {
                    "id": "yyy",
                    "sequence": "GGTT"
                },
                {
                    "id": "recombinant",
                    "sections": [
                        {
                            "from id": "xxx"
                        },
                        {
                            "from id": "yyy"
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (read1, read2, read3) = list(s)
        self.assertEqual("ACCAGGTT", read3.sequence)

    def testOneSequenceSequenceMutated(self):
        """
        A sequence should be be able to be mutated.
        """
        sequence = "A" * 100
        s = Sequences(
            StringIO(
                """[{
            "sequence": "%s",
            "mutation rate": 1.0
        }]
        """
                % sequence
            )
        )
        (read,) = list(s)
        # All bases should have been changed, due to a 1.0 mutation rate.
        diffs = sum((a != b) for (a, b) in zip(sequence, read.sequence))
        self.assertEqual(len(sequence), len(read.sequence))
        self.assertEqual(diffs, len(read.sequence))

    def testRatchet(self):
        """
        The ratchet specification must result in the expected result.
        """
        # Note that this is a very simple test, using a 1.0 mutation rate
        # and a fixed alphabet.
        length = 50
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "orig",
                    "alphabet": "01",
                    "length": %s
                },
                {
                    "count": 2,
                    "from id": "orig",
                    "mutation rate": 1.0,
                    "ratchet": true
                }
            ]
        }"""
                % length
            )
        )
        (orig, mutant1, mutant2) = list(s)
        # The distance from the original to the first mutant must be 100 (i.e.,
        # all bases).
        diffCount = sum(a != b for (a, b) in zip(orig.sequence, mutant1.sequence))
        self.assertEqual(length, diffCount)

        # The distance from the first mutant to the second must be 100 (i.e.,
        # all bases).
        diffCount = sum(a != b for (a, b) in zip(mutant1.sequence, mutant2.sequence))
        self.assertEqual(length, diffCount)

        # The sequences of the original and the second mutant must be
        # identical.
        self.assertEqual(orig.sequence, mutant2.sequence)

    def testReverseComplement(self):
        """
        The reverse complement specification must result in the expected result.
        """
        length = 50
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "orig",
                    "length": %s
                },
                {
                    "from id": "orig",
                    "rc": true
                },
                {
                    "from id": "orig",
                    "reverse complement": true
                }
            ]
        }"""
                % length
            )
        )
        (orig, rc1, rc2) = list(s)
        self.assertEqual(orig.reverseComplement().sequence, rc1.sequence)
        self.assertEqual(orig.reverseComplement().sequence, rc2.sequence)

    def testReverseComplementEntireSequence(self):
        """
        The reverse complement specification must result in the expected result
        when an entire sequence is reverse complemented.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "orig",
                    "length": 25
                },
                {
                    "sections": [
                        {
                            "from id": "orig",
                            "length": 25,
                            "rc": true
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (orig, rc) = list(s)
        self.assertEqual(orig.reverseComplement().sequence, rc.sequence)

    def testReverseComplementSection(self):
        """
        The reverse complement specification must result in the expected result
        when just a section is reverse complemented.
        """
        s = Sequences(
            StringIO(
                """{
            "sequences": [
                {
                    "id": "orig",
                    "length": 100
                },
                {
                    "sections": [
                        {
                            "from id": "orig",
                            "length": 40
                        },
                        {
                            "from id": "orig",
                            "length": 40,
                            "rc": true
                        },
                        {
                            "from id": "orig",
                            "length": 20,
                            "start": 81
                        }
                    ]
                }
            ]
        }"""
            )
        )
        (orig, rc) = list(s)
        print("orig", orig.sequence)
        self.assertEqual(
            orig.sequence[:40]
            + orig[:40].reverseComplement().sequence
            + orig.sequence[80:],
            rc.sequence,
        )
