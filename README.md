ion:
Traceback (most recent call last):
  File "/usr/share/python-wheels/resolvelib-0.5.4-py2.py3-none-any.whl/resolvelib/resolvers.py", line 171, in _merge_into_criterion
    crit = self.state.criteria[name]
KeyError: 'pip'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/share/python-wheels/urllib3-1.26.5-py2.py3-none-any.whl/urllib3/response.py", line 438, in _error_catcher
    yield
  File "/usr/share/python-wheels/urllib3-1.26.5-py2.py3-none-any.whl/urllib3/response.py", line 519, in read
    data = self._fp.read(amt) if not fp_closed else b""
  File "/usr/share/python-wheels/CacheControl-0.12.6-py2.py3-none-any.whl/cachecontrol/filewrapper.py", line 62, in read
    data = self.__fp.read(amt)
  File "/usr/lib/python3.9/http/client.py", line 458, in read
    n = self.readinto(b)
  File "/usr/lib/python3.9/http/client.py", line 502, in readinto
    n = self.fp.readinto(b)
  File "/usr/lib/python3.9/socket.py", line 704, in readinto
    return self._sock.recv_into(b)
  File "/usr/lib/python3.9/ssl.py", line 1241, in recv_into
    return self.read(nbytes, buffer)
  File "/usr/lib/python3.9/ssl.py", line 1099, in read
    return self._sslobj.read(len, buffer)
socket.timeout: The read operation timed out

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/pip/_internal/cli/base_command.py", line 223, in _main
    status = self.run(options, args)
  File "/usr/lib/python3/dist-packages/pip/_internal/cli/req_command.py", line 180, in wrapper
    return func(self, options, args)
  File "/usr/lib/python3/dist-packages/pip/_internal/commands/install.py", line 346, in run
    requirement_set = resolver.resolve(
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/resolver.py", line 122, in resolve
    self._result = resolver.resolve(
  File "/usr/share/python-wheels/resolvelib-0.5.4-py2.py3-none-any.whl/resolvelib/resolvers.py", line 453, in resolve
    state = resolution.resolve(requirements, max_rounds=max_rounds)
  File "/usr/share/python-wheels/resolvelib-0.5.4-py2.py3-none-any.whl/resolvelib/resolvers.py", line 318, in resolve
    name, crit = self._merge_into_criterion(r, parent=None)
  File "/usr/share/python-wheels/resolvelib-0.5.4-py2.py3-none-any.whl/resolvelib/resolvers.py", line 173, in _merge_into_criterion
    crit = Criterion.from_requirement(self._p, requirement, parent)
  File "/usr/share/python-wheels/resolvelib-0.5.4-py2.py3-none-any.whl/resolvelib/resolvers.py", line 82, in from_requirement
    if not cands:
  File "/usr/share/python-wheels/resolvelib-0.5.4-py2.py3-none-any.whl/resolvelib/structs.py", line 124, in __bool__
    return bool(self._sequence)
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/found_candidates.py", line 99, in __bool__
    return any(self)
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/found_candidates.py", line 37, in _insert_installed
    for candidate in others:
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/found_candidates.py", line 78, in <genexpr>
    others = (
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/factory.py", line 239, in iter_index_candidates
    candidate = self._make_candidate_from_link(
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/factory.py", line 167, in _make_candidate_from_link
    self._link_candidate_cache[link] = LinkCandidate(
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/candidates.py", line 296, in __init__
    super(LinkCandidate, self).__init__(
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/candidates.py", line 144, in __init__
    self.dist = self._prepare()
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/candidates.py", line 222, in _prepare
    dist = self._prepare_distribution()
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/candidates.py", line 307, in _prepare_distribution
    return self._factory.preparer.prepare_linked_requirement(
  File "/usr/lib/python3/dist-packages/pip/_internal/operations/prepare.py", line 480, in prepare_linked_requirement
    return self._prepare_linked_requirement(req, parallel_builds)
  File "/usr/lib/python3/dist-packages/pip/_internal/operations/prepare.py", line 503, in _prepare_linked_requirement
    local_file = unpack_url(
  File "/usr/lib/python3/dist-packages/pip/_internal/operations/prepare.py", line 253, in unpack_url
    file = get_http_url(
  File "/usr/lib/python3/dist-packages/pip/_internal/operations/prepare.py", line 130, in get_http_url
    from_path, content_type = download(link, temp_dir.path)
  File "/usr/lib/python3/dist-packages/pip/_internal/network/download.py", line 163, in __call__
    for chunk in chunks:
  File "/usr/lib/python3/dist-packages/pip/_internal/cli/progress_bars.py", line 168, in iter
    for x in it:
  File "/usr/lib/python3/dist-packages/pip/_internal/network/utils.py", line 64, in response_chunks
    for chunk in response.raw.stream(
  File "/usr/share/python-wheels/urllib3-1.26.5-py2.py3-none-any.whl/urllib3/response.py", line 576, in stream
    data = self.read(amt=amt, decode_content=decode_content)
  File "/usr/share/python-wheels/urllib3-1.26.5-py2.py3-none-any.whl/urllib3/response.py", line 541, in read
    raise IncompleteRead(self._fp_bytes_read, self.length_remaining)
  File "/usr/lib/python3.9/contextlib.py", line 135, in __exit__
    self.gen.throw(type, value, traceback)
  File "/usr/share/python-wheels/urllib3-1.26.5-py2.py3-none-any.whl/urllib3/response.py", line 443, in _error_catcher
    raise ReadTimeoutError(self._pool, None, "Read timed out.")
urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='www.piwheels.org', port=443): Read timed out.
robothcc@raspberry:~ $ 
