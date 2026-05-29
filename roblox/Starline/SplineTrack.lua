--!strict
--[[
  Catmull-Rom spline track with arc-length table.
  Waypoints: { Vector3, ... } closed loop (>= 4 points).
]]

local SplineTrack = {}
SplineTrack.__index = SplineTrack

export type SplineTrack = typeof(setmetatable({} :: {
	_waypoints: { Vector3 },
	_pts: { Vector3 },
	_sTab: { number },
	length: number,
}, SplineTrack))

local function catmull(p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3, u: number): Vector3
	local u2 = u * u
	local u3 = u2 * u
	return 0.5
		* (
			(2 * p1)
			+ (-p0 + p2) * u
			+ (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2
			+ (-p0 + 3 * p1 - 3 * p2 + p3) * u3
		)
end

function SplineTrack.new(waypoints: { Vector3 }, samplesPerSegment: number?): SplineTrack
	local spc = samplesPerSegment or 32
	assert(#waypoints >= 4, "need >= 4 waypoints")
	local self = setmetatable({
		_waypoints = waypoints,
		_pts = {},
		_sTab = {},
		length = 0,
	}, SplineTrack)

	local dense: { Vector3 } = {}
	local n = #waypoints
	for i = 1, n do
		local p0 = waypoints[((i - 2) % n) + 1]
		local p1 = waypoints[i]
		local p2 = waypoints[(i % n) + 1]
		local p3 = waypoints[((i + 1) % n) + 1]
		for k = 0, spc - 1 do
			local u = k / spc
			table.insert(dense, catmull(p0, p1, p2, p3, u))
		end
	end

	local sTab = { 0 }
	for i = 2, #dense do
		table.insert(sTab, sTab[#sTab] + (dense[i] - dense[i - 1]).Magnitude)
	end

	self._pts = dense
	self._sTab = sTab
	self.length = sTab[#sTab]
	return self
end

function SplineTrack.oval(radius: number?, height: number?, n: number?): SplineTrack
	local r = radius or 200
	local y = height or 0
	local count = n or 12
	local wp: { Vector3 } = {}
	for i = 0, count - 1 do
		local t = (i / count) * math.pi * 2
		table.insert(wp, Vector3.new(r * math.cos(t), y, r * math.sin(t)))
	end
	return SplineTrack.new(wp)
end

function SplineTrack._interp(self: SplineTrack, s: number): (number, number)
	s = s % self.length
	local idx = 1
	for i = 2, #self._sTab do
		if self._sTab[i] > s then
			idx = i - 1
			break
		end
	end
	local s0 = self._sTab[idx]
	local s1 = self._sTab[idx + 1]
	local t = if s1 > s0 then (s - s0) / (s1 - s0) else 0
	return idx, t
end

function SplineTrack.position(self: SplineTrack, s: number): Vector3
	local idx, t = self:_interp(s)
	return self._pts[idx]:Lerp(self._pts[idx + 1], t)
end

function SplineTrack.tangent(self: SplineTrack, s: number, eps: number?): Vector3
	local e = eps or 0.5
	local fwd = self:position(s + e)
	local bwd = self:position(s - e)
	local tan = fwd - bwd
	if tan.Magnitude < 1e-6 then
		return Vector3.new(1, 0, 0)
	end
	return tan.Unit
end

function SplineTrack.curvature(self: SplineTrack, s: number, eps: number?): number
	local e = eps or 1
	local t0 = self:tangent(s - e, e)
	local t1 = self:tangent(s + e, e)
	return (t1 - t0).Magnitude / (2 * e)
end

return SplineTrack
