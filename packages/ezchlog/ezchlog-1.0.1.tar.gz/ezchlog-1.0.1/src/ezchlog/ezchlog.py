from enum import Enum
from pathlib import Path
from re import match
from re import sub
from subprocess import run
from typing import Optional

from .config import Config


class StrChainSub:
    def __init__(self, s: str) -> None:
        self.s = s

    def sub(self, regex: str, replacement: str) -> 'StrChainSub':
        return StrChainSub(sub(regex, replacement, self.s))

    def __str__(self) -> str:
        return self.s


class EzChLog:
    def __init__(self) -> None:
        self.cfg = Config()

    @staticmethod
    def get_slug(s: str) -> str:
        return str(
            StrChainSub(s.lower())
            .sub(r'\s+', '_')
            .sub(r'\W', '')
            .sub(r'_+', '_'),
        )[:50].strip().strip('_')  # yapf: disable

    def run_command(self, *args: str, **kwargs) -> str:
        ret = run(args, cwd=str(self.cfg.root_dir), capture_output=True, encoding='utf-8', **kwargs)
        if ret.returncode:
            raise ValueError(ret.stderr)
        else:
            return ret.stdout

    def add(self, *, dry_run: bool, message: str, cat: Enum, ref: str, add_to_index: bool) -> tuple[Path, str]:
        first_line = message.split('\n')[0] if '\n' in message else message
        lines = message.split('\n')[1:] if '\n' in message else []
        if not first_line.startswith('- '):
            first_line = '- ' + first_line
        slug = self.get_slug((f'{ref}-' if ref else '') + first_line) + '.md'
        if ref:
            first_line += f" ({ref})"
        lines.insert(0, first_line)
        md_message = '  \n'.join(line.rstrip() for line in lines)
        log_file = self.cfg.log_dir / cat.name / slug
        log_file.parent.mkdir(parents=True, exist_ok=True)
        if not dry_run:
            with log_file.open('w', encoding='utf-8') as f:
                f.write(md_message + '\n')
            if add_to_index:
                self.run_command('git', 'add', str(log_file.relative_to(self.cfg.root_dir)))
        return log_file.relative_to(self.cfg.log_dir), md_message

    def commit(self, *, dry_run: bool, partlog_path: Optional[str]) -> str:
        partlogs = [
            pl[3:] for pl in self.run_command(
                'git',
                'status',
                '--porcelain',
                '--untracked-files=no',
                '--no-renames',
                str(self.cfg.log_dir.relative_to(self.cfg.root_dir)),
            ).split('\n') if pl.startswith('A')
        ]
        if partlog_path:
            # little dance to ensure to have a relative path from root dir
            partlog = str(Path(partlog_path).absolute().relative_to(self.cfg.root_dir))
            if partlog not in partlogs:
                raise ValueError(f"{partlog_path} is not amongst added part log files.")
            partlogs.remove(partlog)
        elif len(partlogs) == 0:
            raise ValueError("No part log file found. Cannot commit for you, use `add` first.")
        elif len(partlogs) == 1:
            partlog = partlogs.pop()
        else:
            raise ValueError("Multiple part log files found. Please specify which one is primary as command line paramater.")
        content = (self.cfg.root_dir / partlog).read_text(encoding='utf-8').split('\n')
        m = match(r'^(- )?(.+?)( \((.+)\))?$', content[0])
        _, message, _, ref = m.groups() if m else (None, content[0].lstrip('- '), None, None)
        assert message is not None
        if ref and ref.startswith('#'):
            ref = f'Ref {ref}'
        commit_message = f'{ref}: {message}\n' if ref else f'{message}\n'
        if content[1:] or partlogs:
            commit_message += '\n'  # blank line
        commit_message += '\n'.join(content[1:])
        for pl in sorted(partlogs):
            commit_message += (self.cfg.root_dir / pl).read_text(encoding='utf-8')
        commit_message = commit_message.strip() + "\n"  # ensure last newline
        if not dry_run:
            self.run_command('git', 'commit', '--file=-', input=commit_message)
        return commit_message

    def list(self) -> list[Path]:
        return [
            p.relative_to(self.cfg.log_dir)
            for cat in list[Enum](self.cfg.category_class)
            for p in sorted((self.cfg.log_dir / cat.name).glob('*.md'))
        ]  # yapf: disable

    def merge(self, *, dry_run: bool, next_version: str, update_index: bool) -> str:
        lines_to_insert = [f"## {next_version}"]
        for cat in list[Enum](self.cfg.category_class):
            new_category = True
            for p in sorted((self.cfg.log_dir / cat.name).glob('*.md')):
                if new_category:
                    lines_to_insert.append(f"### {cat.name}")
                    new_category = False
                lines_to_insert.extend(p.read_text(encoding='utf-8').strip().split('\n'))
                if not dry_run:
                    p.unlink()
                    if update_index:
                        self.run_command('git', 'rm', '-f', '--ignore-unmatch', str(p.relative_to(self.cfg.root_dir)))
        if self.cfg.log_file.exists():
            lines = self.cfg.log_file.read_text(encoding='utf-8').strip().split('\n')
        else:
            if not dry_run:
                self.cfg.log_file.write_text(self.cfg.default_changelog, encoding='utf-8')
            lines = self.cfg.default_changelog.strip().split('\n')
        if len(lines_to_insert) >= 2:
            pos = 0
            for i, line in enumerate(lines):
                if line.startswith('## '):
                    pos = i
                    break
            else:
                pos = -1
            if pos == -1:
                lines.append("")
                lines.extend(lines_to_insert)
            else:
                lines_to_insert.append("")
                lines = lines[0:pos] + lines_to_insert + lines[pos:]
        changelog = '\n'.join(lines) + '\n'
        if not dry_run:
            self.cfg.log_file.write_text(changelog, encoding='utf-8')
            if update_index:
                self.run_command('git', 'add', str(self.cfg.log_file.relative_to(self.cfg.root_dir)))
        return changelog
