-- Roblox UGC Helper Plugin
-- Only runs in Studio
local toolbar = plugin:CreateToolbar("UGC Helper")
local button = toolbar:CreateButton("Create UGC", "Adds Handle+HatAttachment to your mesh", "")

button.Click:Connect(function()
	local selection = game:GetService("Selection")
	local meshPart = selection:Get()[1]
	if meshPart and meshPart:IsA("MeshPart") then
		local accessory =  Instance.new("Accessory"); accessory.Name = "UGC"
		local handle = meshPart:Clone(); handle.Name = "Handle"; handle.Parent = accessory
		local att = Instance.new("Attachment"); att.Name =  "HatAttachment"; att.Parent = handle
		accessory.Parent = workspace
		selection:Set({accessory})
	end
end)
