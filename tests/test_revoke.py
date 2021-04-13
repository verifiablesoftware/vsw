from vsw.commands import revoke
def test_execute_revoke():
    revoke.revoke("cc2a2758-45c5-4295-93a5-77ef5c383df1", None, None, True)