--!strict
local Config = require(script.Parent.Config)

export type FlowState = "unstable" | "stable" | "resonant" | "flow"

local Flow = {}

export type FlowMachine = { state: FlowState }

local function C(cfg: any?): any
	return cfg or Config
end

function Flow.newMachine(): FlowMachine
	return { state = "unstable" }
end

function Flow.update(machine: FlowMachine, c: number, R: number, cfg: any?): FlowState
	local cfgC = C(cfg)
	local s = machine.state
	if s == "flow" then
		if c < cfgC.FlowExitFlowC or R < cfgC.FlowExitFlowR then
			s = if c >= cfgC.FlowExitResonantC then "resonant" else "stable"
		end
	elseif s == "resonant" then
		if c > cfgC.FlowEnterFlowC and R > cfgC.FlowEnterFlowR then
			s = "flow"
		elseif c < cfgC.FlowExitResonantC then
			s = if c >= cfgC.FlowExitStableC then "stable" else "unstable"
		end
	elseif s == "stable" then
		if c > cfgC.FlowEnterFlowC and R > cfgC.FlowEnterFlowR then
			s = "flow"
		elseif c > cfgC.FlowEnterResonantC then
			s = "resonant"
		elseif c < cfgC.FlowExitStableC then
			s = "unstable"
		end
	else
		if c > cfgC.FlowEnterFlowC and R > cfgC.FlowEnterFlowR then
			s = "flow"
		elseif c > cfgC.FlowEnterResonantC then
			s = "resonant"
		elseif c > cfgC.FlowEnterStableC then
			s = "stable"
		end
	end
	machine.state = s
	return s
end

return Flow
