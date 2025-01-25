import json
import shlex
import typing as t
import warnings
import xml.etree.ElementTree as ElementTree


class Message:
    """Meta message handler class.

    This class can be used instead of `MessageXml` or `MessageJson`, when it is
    not known, which type of message is received. Automatically detect
    the type of the message and then behave like `MessageXml` or `MessageJson`.

    Attributes
    ----------
    msg_meth : MessageXml | MessageJson
        The message method, which `Message` should behave like.

    """

    def __init__(self, msg: bytes) -> None:
        """Determine which type of message is received.

        Parameters
        ----------
        msg
            Depending on the content of msg, either set `msg_meth`
            to an instance of `MessageXml` or `MessageJson`

        Raises
        ------
        Exception
            When the received message is in an unknown format or does not
            fullfill the needs for the xml or json message.

        """
        if msg.strip().startswith(b"<nap>"):
            self.msg_meth = MessageXml()  # type: t.Union[MessageXml, MessageJson]
        elif msg.strip().startswith(b"{"):
            self.msg_meth = MessageJson()
        else:
            raise Exception("Received unknown message format.")

    def __getattr__(self, name: str) -> t.Any:
        """Make this class behave like `MessageXml` or `MessageJson`.

        Parameters
        ----------
        name
            Name of the function, that should be called from `MessageXml` or
            `MessageJson`.

        Returns
        -------
        Return what the function of the composed class return.

        """
        return getattr(self.msg_meth, name)

    @staticmethod
    def dict_to_argslist(d: dict) -> list:
        """Convert the dict with the main `parser` arguments into a list.

        The function `parser.parse_args` needs a list as input with the arguments
        as input, but the received message from the client is converted into a
        dict. So this function converts the dict into a list to get the arguments
        for the `parser`.

        Additionally, clean the arguments. E.g. an argument can be `--x 1`, but
        xml syntax forbids `<--x>1</--x>`. To overcome this, underscore instead
        of dash can be used: `<__x>1</__x>`.

        ANNOTATION: DO NOT USE ARGUMENTS FOR THE MAIN PARSER THAT START WITH
                    UNDERSCORE, BECAUSE THEY WILL BE CONVERTED INTO DASH.

        Parameters
        ----------
        d
            Dirty arguments for the main `parser`.

        Returns
        -------
        Clean list with arguments for the `main` parser.

        """
        lst = []
        for key, value in d.items():
            k = key.lstrip("_")
            dash = "-" * (len(key) - len(k))
            k = dash + k
            if value:
                if type(value) is list:
                    for val in value:
                        if val:
                            lst.append(f"{k} {val}")
                        else:
                            lst.append(k)
                else:
                    lst.append(f"{k} {value}")
            else:
                lst.append(k)
        return shlex.split(" ".join(lst))


class MessageXml:
    """Handle xml messages."""

    @staticmethod
    def _to_dict(xml: t.Union[bytes, str]) -> dict:
        """Convert bytes / a string with xml syntax into a dict.

        Parameters
        ----------
        xml
            The xml formatted bytes/string.

        Raises
        ------
        Exception
            Root element of xml must be <nap>.

        Returns
        -------
        A dict with the keys of the xml tags and its texts as values.

        """
        root = ElementTree.fromstring(xml)

        if root.tag != "nap":
            raise Exception("Root must be named `nap`. Message must be in `<nap>...</nap>`.")

        ret = {}  # type: t.Dict[t.Any, t.Any]
        for child in root:
            if child.tag in ret:
                if type(ret[child.tag]) is not list:
                    ret[child.tag] = [ret[child.tag], child.text]
                else:
                    ret[child.tag].append(child.text)
            else:
                ret[child.tag] = child.text
        return ret

    @staticmethod
    def _from_dict(d: dict, top: bool = True) -> str:
        """Convert a dictionary into xml formatted str.

        The dict MUST only contain a dictionary, string or any other
        non-iterable (convertable to str and json serializable) as value.
        This rule applies recursively to all nested dictionaries.

        Parameters
        ----------
        d
            Dictionary, that should be converted in an xml styled str.
        top
            True: The function is at the highest level of the dict
                  and therefore must return its elements.
            False: The function iterates through some nested dictionaries,
                   so the root element itself is returned and further processed
                   to add the entries from the nested dictionary.

        Raises
        ------
        Exception
            The function started by NetArgumentParser does not return a
            dictionary but NetArgumentParser should autoformat the return.

        Returns
        -------
        The xml styled str with tags of the dict keys and its values as texts.

        """
        if type(d) is not dict:
            raise Exception("Cannot autoformat non-dict. Check return of the function started by NetArgumentParser.")
        json.dumps(d)  # evil cross call to have same restrictions in both message formats

        root = ElementTree.Element("root")
        for key, val in d.items():
            if type(val) is dict:
                root_sub = MessageXml._from_dict(val, False)
                sub_element = ElementTree.SubElement(root, key)
                for element in root_sub:
                    # mypy does not recognize, that when `False` is given to
                    # from_dict, only ElementTree.Element can be returned. So
                    # _from_dict(...) -> t.Union[str, ElementTree.Element] would
                    # not help, since sub_element.append wants only the Element
                    # type. Furthermore, this type hint would cause a clutter
                    # for all non recursive calls that expect just a string.
                    sub_element.append(element)  # type: ignore[arg-type]
            else:
                ElementTree.SubElement(root, key).text = str(val)
        if top:
            return "".join(ElementTree.tostring(e, encoding="unicode") for e in root)
        else:
            # only used for recursive calls to iterate through nested dicts
            return root  # type: ignore[return-value]

    @staticmethod
    def _replace_breaking_chars(string: str) -> str:
        """Replace xml breaking characters with xml unbreaking characters."""
        return string.replace("<", "[").replace(">", "]")

    @staticmethod
    def _end_of_msg(string: bytes) -> bool:
        """Determine, if the received message is complete.

        The message from the client is received in chunks, and to determine
        whether the message is complete, this function checks if the root
        element of the xml message is closed.

        Parameters
        ----------
        string
            The message, that was received by the client so far.

        Returns
        -------
        Whether the message is fully received.

        """
        return string.strip().endswith(b"</nap>")

    def _format(self, autoformat: bool, resp: t.Union[dict, str], exc: str) -> bytes:
        """Format the message to be sent to the client.

        Parameters
        ----------
        autoformat
            True: resp must be a dict and is converted into xml string, where
                  the keys of the dict will be xml tags and the values of the
                  dict will be the xml texts.
            False: resp will be sent to the client "as is".
        resp
            The information that should be sent in the response section.
        exc
            The information that should be sent in the exception section.

        Returns
        -------
        Message that is sent to the client.

        """
        r = ""  # type: t.Union[dict, str]
        e = self._replace_breaking_chars(exc)
        if resp != "":
            try:
                # a wrong type is handled within _from_dict
                r = self._from_dict(resp) if autoformat else resp  # type: ignore[arg-type]
            except Exception as e1:
                e = self._replace_breaking_chars(str(e1))
                warnings.warn(str(e1))
        return "<nap><response>{}</response><exception>{}</exception><finished>1</finished></nap>".format(r, e).encode("utf-8")


class MessageJson:
    """Handle json messages."""

    @staticmethod
    def _to_dict(json_string: t.Union[bytes, str]) -> dict:
        """Convert bytes / a string with json syntax into a dict.

        Parameters
        ----------
        json_string
            The json formatted bytes/string.

        Returns
        -------
        A dict with the keys of the json keys and its values.

        """
        return json.loads(json_string)

    @staticmethod
    def _from_dict(d: dict) -> str:
        """Convert a dict into a json formatted str.

        The dict MUST only contain a dictionary, string or any other
        non-iterable (convertable to str and json serializable) as value.
        This rule applies recursively to all nested dictionaries.

        Parameters
        ----------
        d
            Dictionary, that should be converted a json styled str.

        Returns
        -------
        The json styled str with keys of the dict keys and its values.

        """
        MessageXml._from_dict(d)  # evil cross call to have same restrictions in both message formats
        return json.dumps(d)

    @staticmethod
    def _replace_breaking_chars(string: str) -> str:
        """Replace json breaking characters with json unbreaking characters."""
        return string.replace('"', "'")

    @staticmethod
    def _end_of_msg(string: bytes) -> bool:
        """Determine, if the received message is complete.

        The message from the client is received in chunks, and to determine
        whether the message is complete, this function checks if the number of
        opening `{` equals the number of closed `}`.

        ANNOTATION: DO NOT SEND STRING ARGUMENTS WITH INCOMPLETE
                    CURLY PARENTHESES.

        Parameters
        ----------
        string
            The message, that was received by the client so far.

        Returns
        -------
        Whether the message is fully received.

        """
        return string.count(b"{") == string.count(b"}")

    def _format(self, autoformat: bool, resp: t.Union[dict, str], exc: str) -> bytes:
        """Format the message to be sent to the client.

        Parameters
        ----------
        autoformat
            True: resp must be a dict and is converted into a json string, where
                  the keys of the dict will be json keys and the values of the
                  dict will be the json keys texts.
            False: resp will be sent to the client "as is".
        resp
            The information that should be sent in the response section.
        exc
            The information that should be sent in the exception section.

        Returns
        -------
        Message that is sent to the client.

        """
        r = '""'  # type: t.Union[dict, str]
        e = self._replace_breaking_chars(exc)
        if resp != "":
            try:
                # a wrong type is handled within _from_dict
                r = self._from_dict(resp) if autoformat else resp  # type: ignore[arg-type]
            except Exception as e1:
                e = self._replace_breaking_chars(str(e1))
                warnings.warn(str(e1))
        return '{{"response": {}, "exception": "{}", "finished": 1}}'.format(r, e).encode("utf-8")
