var player;
var majhongDropConfig = {
	"source": {
		"group": {
			"id": "1203ae6f-32e1-46a1-b01f-43ee1631ab87",
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
    player = new NanoPlayer("majhongDropPlayer");
    player.setup(majhongDropConfig).then(function (majhongDropConfig) {
        console.log("setup success");
        console.log("majhongDropConfig: " + JSON.stringify(majhongDropConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});