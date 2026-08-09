var player;
var kingRoyalConfig = {
	"source": {
		"group": {
			"id": "558654bc-b7d9-4e2c-9d28-f8aad5ef1203",
			"apiurl": "https://bintu.nanostream.cloud"
		},
		"options": {
			"adaption": {
				"rule": "deviationOfMean2"
			}
		},
		"startIndex": 0
	},
	"playback": {
		"enableMediaOverQuic": true,
		"latencyControlMode": "balancedadaptive",
		"autoplay": true,
		"automute": true,
		"faststart": true
	},
	"style": {
		"width": "auto",
		"height": "auto"
	}
};
document.addEventListener('DOMContentLoaded', function () {
    player = new NanoPlayer("kingRoyalPlayer");
    player.setup(kingRoyalConfig).then(function (kingRoyalConfig) {
        console.log("setup success");
        console.log("kingRoyalConfig: " + JSON.stringify(kingRoyalConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});