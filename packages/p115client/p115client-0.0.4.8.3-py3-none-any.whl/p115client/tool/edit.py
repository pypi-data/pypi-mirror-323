#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__all__ = [
    "update_abstract", "update_desc", "update_star", "update_label", "update_score", 
    "update_top", "update_show_play_long", "update_category_shortcut", 
]
__doc__ = "这个模块提供了一些和修改文件或目录信息有关的函数"

from collections.abc import Iterable, Iterator, Sequence
from functools import partial
from itertools import batched, pairwise
from typing import overload, Any, Literal

from concurrenttools import taskgroup_map, threadpool_map
from iterutils import chunked, run_gen_step, through, async_through
from p115client import check_response, P115Client


def update_abstract(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    method: str, 
    value: Any, 
    batch_size: int = 10_000, 
    max_workers: None | int = None, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量设置文件或目录

    :param client: 115 客户端或 cookies
    :param ids: 一组文件或目录的 id
    :param method: 方法名
    :param value: 要设置的值
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param max_workers: 并发工作数，如果为 None 或者 <= 0，则自动确定
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    if not isinstance(client, P115Client):
        client = P115Client(client, check_for_relogin=True)
    if max_workers is None or max_workers <= 0:
        max_workers = 20 if async_ else None
    def gen_step():
        setter = partial(getattr(client, method), async_=async_, **request_kwargs)
        def call(batch, /):
            return check_response(setter(batch, value))
        if max_workers == 1:
            for batch in chunked(ids, batch_size):
                yield call(batch)
        elif async_: 
            yield async_through(taskgroup_map(
                call, 
                chunked(ids, batch_size), 
                max_workers=max_workers, 
            ))
        else:
            through(threadpool_map(
                call, 
                chunked(ids, batch_size), 
                max_workers=max_workers
            ))
    return run_gen_step(gen_step, async_=async_)


def update_desc(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    desc: str = "", 
    batch_size: int = 10_000, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量给文件或目录设置备注，此举可更新此文件或目录的 mtime

    :param client: 115 客户端或 cookies
    :param ids: 一组文件或目录的 id
    :param desc: 备注文本
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    return update_abstract(
        client, 
        ids, 
        method="fs_desc_set", 
        value=desc, 
        batch_size=batch_size, 
        async_=async_, 
        **request_kwargs, 
    )


def update_star(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    star: bool = True, 
    batch_size: int = 10_000, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量给文件或目录设置星标

    .. note::
        如果一批中有任何一个 id 已经被删除，则这一批直接失败报错

    :param client: 115 客户端或 cookies
    :param ids: 一组文件或目录的 id
    :param star: 是否设置星标
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    return update_abstract(
        client, 
        ids, 
        method="fs_star_set", 
        value=star, 
        batch_size=batch_size, 
        async_=async_, 
        **request_kwargs, 
    )


def update_label(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    label: int | str = "1", 
    batch_size: int = 10_000, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量给文件或目录设置标签

    :param client: 115 客户端或 cookies
    :param ids: 一组文件或目录的 id
    :param label: 标签 id，多个用逗号 "," 隔开，如果用一个根本不存在的 id，效果就是清空标签列表
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    return update_abstract(
        client, 
        ids, 
        method="fs_label_set", 
        value=label, 
        batch_size=batch_size, 
        async_=async_, 
        **request_kwargs, 
    )


def update_score(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    score: int = 0, 
    batch_size: int = 10_000, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量给文件或目录设置分数

    :param client: 115 客户端或 cookies
    :param ids: 一组文件或目录的 id
    :param score: 分数
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    return update_abstract(
        client, 
        ids, 
        method="fs_score_set", 
        value=score, 
        batch_size=batch_size, 
        async_=async_, 
        **request_kwargs, 
    )


def update_top(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    top: bool = True, 
    batch_size: int = 10_000, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量给文件或目录设置置顶

    :param client: 115 客户端或 cookies
    :param ids: 一组文件或目录的 id
    :param score: 分数
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    return update_abstract(
        client, 
        ids, 
        method="fs_top_set", 
        value=top, 
        batch_size=batch_size, 
        async_=async_, 
        **request_kwargs, 
    )


def update_show_play_long(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    show: bool = True, 
    batch_size: int = 10_000, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量给目录设置显示时长

    :param client: 115 客户端或 cookies
    :param ids: 一组目录的 id
    :param show: 是否显示时长
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    return update_abstract(
        client, 
        ids, 
        method="fs_show_play_long_set", 
        value=show, 
        batch_size=batch_size, 
        async_=async_, 
        **request_kwargs, 
    )


def update_category_shortcut(
    client: str | P115Client, 
    ids: Iterable[int | str], 
    /, 
    set: bool = True, 
    batch_size: int = 10_000, 
    *, 
    async_: Literal[False, True] = False, 
    **request_kwargs, 
):
    """批量给目录设置显示时长

    :param client: 115 客户端或 cookies
    :param ids: 一组目录的 id
    :param set: 是否设为快捷入口
    :param batch_size: 批次大小，分批次，每次提交的 id 数
    :param async_: 是否异步
    :param request_kwargs: 其它请求参数
    """
    return update_abstract(
        client, 
        ids, 
        method="fs_category_shortcut_set", 
        value=set, 
        batch_size=batch_size, 
        async_=async_, 
        **request_kwargs, 
    )

