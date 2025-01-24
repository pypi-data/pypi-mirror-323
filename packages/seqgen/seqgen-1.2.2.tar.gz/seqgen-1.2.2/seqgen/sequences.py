import sys
from json import load
from random import choice, uniform

from dark.aaVars import AA_LETTERS
from dark.fasta import FastaReads
from dark.reads import DNARead


class Sequences(object):
    """
    Create genetic sequences from a JSON specification.

    @param spec: A C{str} filename or an open file pointer to read the
        specification from.
    @raise json.decoder.JSONDecodeError: If the specification JSON cannot
        be read.
    @raise ValueError: If the specification JSON is an object but does not
        have a 'sequences' key.
    """

    NT = list("ACGT")
    AA = list(AA_LETTERS)
    DEFAULT_LENGTH = 100
    DEFAULT_ID_PREFIX = "seq-id-"
    DEFAULT_QUALITY = 30
    LEGAL_SPEC_KEYS = {
        "alphabet",
        "count",
        "description",
        "id",
        "id prefix",
        "filename",
        "format",
        "from id",
        "length",
        "mutation rate",
        "rc",
        "reverse complement",
        "random aa",
        "random nt",
        "ratchet",
        "sections",
        "sequence",
        "sequence file",
        "skip",
    }
    LEGAL_SPEC_SECTION_KEYS = {
        "alphabet",
        "from id",
        "length",
        "mutation rate",
        "random aa",
        "random nt",
        "rc",
        "reverse complement",
        "start",
        "sequence",
        "sequence file",
    }

    def __init__(
        self,
        spec,
        defaultLength=None,
        defaultIdPrefix=None,
        defaultQuality=None,
        _format="fasta",
    ):
        self._defaultLength = defaultLength or self.DEFAULT_LENGTH
        self._defaultIdPrefix = defaultIdPrefix or self.DEFAULT_ID_PREFIX
        self._readSpecification(spec)
        self._idPrefixCount = {}
        self._sequences = {}
        self._format = _format

        defaultQuality = (
            self.DEFAULT_QUALITY if defaultQuality is None else int(defaultQuality)
        )
        # Make sure we have a valid quality.
        assert 0 <= defaultQuality <= 94  # This is 126 - 32 (tilde - space).
        self._defaultQuality = chr(ord("!") + defaultQuality)

    def _readSpecification(self, spec):
        """
        Read the specification in C{spec}.

        @param spec: A C{str} filename or an open file pointer to read the
            specification from.
        @raise KeyError: if the specification JSON is an object and does not
            have a 'sequences' key.
        """
        if isinstance(spec, str):
            with open(spec) as fp:
                j = load(fp)
        elif isinstance(spec, dict):
            j = spec
        else:
            j = load(spec)

        if isinstance(j, list):
            vars_, sequenceSpecs = {}, j
        else:
            try:
                vars_, sequenceSpecs = j.get("variables", {}), j["sequences"]
            except KeyError:
                raise ValueError(
                    "The specification JSON must have a " "'sequences' key."
                )

        self._vars = vars_
        self._sequenceSpecs = list(map(self._expandSpec, sequenceSpecs))
        self._checkKeys()
        self._checkValid()

    def _checkValid(self):
        """
        Check that all specification dicts contain sensible values.

        @param sequenceSpec: A C{dict} with information about the sequences
            to be produced.
        @raise ValueError: If any problem is found.
        """
        ids = set()
        for specCount, spec in enumerate(self._sequenceSpecs, start=1):
            if spec.get("ratchet"):
                nSequences = spec.get("count", 1)
                if nSequences == 1:
                    raise ValueError(
                        "Sequence specification %d is specified as ratchet "
                        "but its count is only 1." % specCount
                    )

                if "mutation rate" not in spec:
                    raise ValueError(
                        "Sequence specification %d is specified as ratchet "
                        "but does not give a mutation rate." % specCount
                    )

            nSequences = spec.get("count", 1)

            try:
                id_ = spec["id"]
            except KeyError:
                pass
            else:
                # If an id is given, the number of sequences requested must be
                # one.
                if nSequences != 1:
                    raise ValueError(
                        "Sequence specification %d with id '%s' has a count "
                        "of %d. If you want to specify a sequence with an "
                        "id, the count must be 1. To specify multiple "
                        "sequences with an id prefix, use 'id prefix'."
                        % (specCount, id_, nSequences)
                    )

                if id_ in ids:
                    raise ValueError(
                        "Sequence specification %d has an id (%s) that has "
                        "already been used." % (specCount, id_)
                    )

                ids.add(id_)

    def _checkKeys(self):
        """
        Check that all specification dicts only contain legal keys.

        @param sequenceSpec: A C{dict} with information about the sequences
            to be produced.
        @raise ValueError: If an unknown key is found.
        """
        for specCount, spec in enumerate(self._sequenceSpecs, start=1):
            unexpected = set(spec) - self.LEGAL_SPEC_KEYS
            if unexpected:
                raise ValueError(
                    "Sequence specification %d contains %sunknown key%s: %s."
                    % (
                        specCount,
                        "an " if len(unexpected) == 1 else "",
                        "" if len(unexpected) == 1 else "s",
                        ", ".join(sorted(unexpected)),
                    )
                )
            try:
                sections = spec["sections"]
            except KeyError:
                pass
            else:
                for sectionCount, section in enumerate(sections, start=1):
                    unexpected = set(section) - self.LEGAL_SPEC_SECTION_KEYS
                    if unexpected:
                        raise ValueError(
                            "Section %d of sequence specification %d contains "
                            "%sunknown key%s: %s."
                            % (
                                sectionCount,
                                specCount,
                                "an " if len(unexpected) == 1 else "",
                                "" if len(unexpected) == 1 else "s",
                                ", ".join(sorted(unexpected)),
                            )
                        )

    def _expandSpec(self, sequenceSpec):
        """
        Recursively expand all string values in a sequence specification.

        @param sequenceSpec: A C{dict} with information about the sequences
            to be produced.
        @return: A C{dict} with all string values expanded.
        """
        new = {}
        for k, v in sequenceSpec.items():
            if isinstance(v, str):
                value = v % self._vars
                # If a substitution was done, see if we can cast the
                # converted string to an int or a float.
                if value != v:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass

            elif isinstance(v, dict):
                value = self._expandSpec(v)
            else:
                value = v
            new[k] = value
        return new

    def _specToDNARead(self, spec, previousRead=None):
        """
        Get a sequence from a specification.

        @param spec: A C{dict} with keys/values specifying a sequence.
        @param previousRead: If not C{None}, a {dark.Read} instance containing
            the last read this method returned. This is only used when
            'ratchet' is given for a specification, in which case we generate
            a mutant based on the previous read.
        @raise ValueError: If the section spec refers to a non-existent other
            sequence, or to part of another sequence but the requested part
            exceeds the bounds of the other sequence. Or if the C{spec} does
            not have a 'length' key when no other sequence is being referred
            to.
        @return: A C{dark.Read} instance.
        """
        alphabet = self.NT
        length = spec.get("length", self._defaultLength)

        if spec.get("ratchet") and previousRead:
            read = DNARead(None, previousRead.sequence)
            alphabet = previousRead.alphabet

        elif "from id" in spec:
            fromId = spec["from id"]
            try:
                fromRead = self._sequences[fromId]
            except KeyError:
                raise ValueError(
                    "Sequence section refers to the id '%s' of "
                    "non-existent other sequence." % fromId
                )
            else:
                # The start offset in the spec is 1-based. Convert to 0-based.
                index = int(spec.get("start", 1)) - 1
                # Use the given length (if any) else the length of the
                # named read.
                length = spec.get("length", len(fromRead))
                sequence = fromRead.sequence[index : index + length]
                alphabet = fromRead.alphabet

                if len(sequence) != length:
                    raise ValueError(
                        "Sequence specification refers to sequence id '%s', "
                        "starting at index %d with length %d, but sequence "
                        "'%s' is not long enough to support that."
                        % (fromId, index + 1, length, fromId)
                    )

                read = DNARead(None, sequence)

        elif "sequence" in spec:
            read = DNARead(None, spec["sequence"])

        elif "sequence file" in spec:
            reads = iter(FastaReads(spec["sequence file"]))
            try:
                read = next(reads)
            except StopIteration:
                raise ValueError("Sequence file '%s' is empty." % spec["sequence file"])
            except FileNotFoundError:
                raise ValueError(
                    "Sequence file '%s' could not be read." % spec["sequence file"]
                )
            if spec.get("id"):
                # There is an id in the spec, which means we are supposed to
                # replace the one that was in the file. Set the id to None
                # and let our caller take care of putting the wanted id in.
                read.id = None

        elif spec.get("alphabet"):
            alphabet = spec["alphabet"]
            read = DNARead(None, "".join(choice(alphabet) for _ in range(length)))

        elif spec.get("random aa"):
            alphabet = self.AA
            read = DNARead(None, "".join(choice(alphabet) for _ in range(length)))

        else:
            read = DNARead(None, "".join(choice(alphabet) for _ in range(length)))

        if "rc" in spec or "reverse complement" in spec:
            read = read.reverseComplement()

        try:
            rate = spec["mutation rate"]
        except KeyError:
            pass
        else:
            read.sequence = self._mutate(read.sequence, rate, alphabet)

        read.alphabet = alphabet

        return read

    def _mutate(self, sequence, rate, alphabet):
        """
        Mutate a sequence at a certain rate.

        @param sequence: A C{str} nucleotide or amino acid sequence.
        @param rate: A C{float} mutation rate.
        @param alphabet: A C{list} of alphabet letters.
        @return: The mutatated C{str} sequence.
        """
        result = []
        possibles = set(alphabet)
        for current in sequence:
            if uniform(0.0, 1.0) < rate:
                result.append(choice(list(possibles - {current})))
            else:
                result.append(current)

        return "".join(result)

    def _readsForSpec(self, spec):
        """
        Yield reads for a given specification.

        @param sequenceSpec: A C{dict} with information about the sequences
            to be produced.
        """
        alphabet = None
        previousRead = None
        nSequences = spec.get("count", 1)

        for count in range(nSequences):
            id_ = None
            if "sections" in spec:
                sequence = ""
                for section in spec["sections"]:
                    read = self._specToDNARead(section, previousRead)
                    sequence += read.sequence
                    if alphabet is None:
                        alphabet = read.alphabet
            else:
                read = self._specToDNARead(spec, previousRead)
                sequence = read.sequence
                id_ = read.id
                alphabet = read.alphabet

            if id_ is None:
                try:
                    id_ = spec["id"]
                except KeyError:
                    prefix = spec.get("id prefix", self._defaultIdPrefix)
                    prefixCount = self._idPrefixCount.setdefault(prefix, 0) + 1
                    self._idPrefixCount[prefix] += 1
                    id_ = "%s%d" % (prefix, prefixCount)

            try:
                id_ = id_ + " " + spec["description"]
            except KeyError:
                pass

            if spec.get("format", self._format).lower() == "fastq":
                quality = self._defaultQuality * len(sequence)
            else:
                quality = None

            read = DNARead(id_, sequence, quality)
            read.alphabet = alphabet

            if id_ in self._sequenceSpecs:
                raise ValueError("Sequence id '%s' has already been used." % id_)
            else:
                self._sequences[id_] = read

            if not spec.get("skip"):
                yield (read, spec.get("filename"))
                previousRead = read

    def __iter__(self):
        """
        Yield the reads, ignoring output files.
        """
        for sequenceSpec in self._sequenceSpecs:
            for read, filename in self._readsForSpec(sequenceSpec):
                yield read

    def write(self):
        """
        Write out all reads, respecting filenames given in the specification.
        """
        filesSeen = set()
        currentFile = currentFp = None
        for sequenceSpec in self._sequenceSpecs:
            for read, thisFile in self._readsForSpec(sequenceSpec):
                if thisFile is None:
                    # Write to standard output.
                    if currentFile:
                        # We already had an open non-stdout file.
                        assert currentFp
                        currentFp.close()
                        currentFp = None
                    currentFile = None
                    currentFp = sys.stdout
                else:
                    # Write to a file.
                    if thisFile == currentFile:
                        assert currentFp
                    else:
                        if currentFile:
                            assert currentFp
                            currentFp.close()
                        currentFp = open(
                            thisFile, "a" if thisFile in filesSeen else "w"
                        )
                        currentFile = thisFile
                        filesSeen.add(thisFile)

                print(
                    read.toString(format_="fasta" if read.quality is None else "fastq"),
                    end="",
                    file=currentFp,
                )
