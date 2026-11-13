import subprocess
from pathlib import Path

from calendario_bot.publisher import Publisher


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def make_clone(tmp_path, name, remote):
    clone = tmp_path / name
    git(tmp_path, "clone", "-q", str(remote), name)
    git(clone, "config", "user.email", "t@example.com")
    git(clone, "config", "user.name", "Test")
    return clone


def setup_repos(tmp_path):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    seed = make_clone(tmp_path, "seed", remote)
    (seed / "data").mkdir()
    (seed / "data" / "events.json").write_text("[]\n")
    git(seed, "add", ".")
    git(seed, "commit", "-q", "-m", "init")
    git(seed, "push", "-q", "origin", "HEAD:main")
    return remote, make_clone(tmp_path, "bot", remote), make_clone(tmp_path, "other", remote)


async def test_publish_pushes_commit(tmp_path):
    remote, bot, _ = setup_repos(tmp_path)
    (bot / "data" / "events.json").write_text("[1]\n")
    publisher = Publisher(bot)
    await publisher.publish("update")
    assert await publisher.sync() is True
    assert git(tmp_path, "--git-dir", str(remote), "log", "--format=%s", "main").splitlines()[0] == "update"


async def test_publish_without_changes_does_not_commit(tmp_path):
    _, bot, _ = setup_repos(tmp_path)
    publisher = Publisher(bot)
    await publisher.publish("nothing")
    assert git(bot, "log", "--format=%s").splitlines() == ["init"]


async def test_conflict_is_notified_once_and_commit_kept(tmp_path):
    _, bot, other = setup_repos(tmp_path)
    (other / "data" / "events.json").write_text("[2]\n")
    git(other, "commit", "-qam", "other")
    git(other, "push", "-q")
    (bot / "data" / "events.json").write_text("[1]\n")

    messages = []

    async def notify(text):
        messages.append(text)

    publisher = Publisher(bot, notify=notify)
    await publisher.publish("mine")
    await publisher.sync()
    await publisher.sync()
    assert await publisher.sync() is False
    assert len(messages) == 1
    assert git(bot, "log", "--format=%s").splitlines()[0] == "mine"
    assert git(bot, "status", "--porcelain") == ""  # rebase was aborted
