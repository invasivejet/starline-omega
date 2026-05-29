--!strict
--[[
  Optional HTTP telemetry POST for local field research.
  Set player attribute StarlineTelemetryUrl or workspace attribute of same name.
  Requires HttpService + HTTP enabled on experience (published or Studio).
]]

local HttpService = game:GetService("HttpService")
local RunService = game:GetService("RunService")

local TelemetrySink = {}

local _accum = 0
local _interval = 5.0

function TelemetrySink.getUrl(player: Player): string?
	local u = player:GetAttribute("StarlineTelemetryUrl")
	if typeof(u) == "string" and u ~= "" then
		return u
	end
	local w = workspace:GetAttribute("StarlineTelemetryUrl")
	if typeof(w) == "string" and w ~= "" then
		return w
	end
	if RunService:IsStudio() then
		return "http://127.0.0.1:8765/telemetry"
	end
	return nil
end

function TelemetrySink.post(player: Player, payload: { [string]: any })
	local url = TelemetrySink.getUrl(player)
	if not url then
		return
	end
	task.spawn(function()
		pcall(function()
			HttpService:PostAsync(url, HttpService:JSONEncode(payload), Enum.HttpContentType.ApplicationJson)
		end)
	end)
end

function TelemetrySink.maybeFlush(player: Player, summary: { [string]: any }, dt: number)
	_accum += dt
	if _accum < _interval then
		return
	end
	_accum = 0
	TelemetrySink.post(player, {
		userId = player.UserId,
		name = player.Name,
		t = os.time(),
		summary = summary,
	})
end

return TelemetrySink
