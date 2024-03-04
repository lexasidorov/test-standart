
// $(document).ready(function () {
	let myMap;
    let placemarks = [];
    let diffPts = [];
	ymaps.ready(init).then(function() {
		console.log('Ready.');
	});
    function getCoordsDiffPts(obj, i) { // works with diffPts format
        let count = Object.values(Object.values(obj)[0]).length;
        return Object.values(Object.values(obj)[0][i])[0]; //array
    }
    async function init(){
        myMap = new ymaps.Map("ymaps", {
            center: [55.76, 37.64],
            zoom: 7
        });
        console.log('Init done.');

        let ptsData = await load_pts();

        if (ptsData["diffPts"]) {
            let colors = [
                '#ff0000',
                '#ff8100',
                '#ffd400',
                '#9dff00',
                '#00ff14',
                '#00ffa1',
                '#00e7ff',
                '#0072ff',
                '#4b00ff',
                '#b400ff',
                '#ff00c8',
                '#ff0052',
                '#ffffff',
                '#000000',
                '#333333',
                '#555555',
                '#777777',
                '#999999',
                '#bbbbbb',
                '#dddddd'
            ];
            let j = 0;
            for (let key of Object.keys(ptsData["diffPts"])) {
                var color = colors[j];
                diffPts.push({[key]: ptsData["diffPts"][key]});
                let innerKey = Object.keys(ptsData["diffPts"][key][0])[0];
                let coordsArr = Object.values(ptsData["diffPts"][key]);
                let obj = {};
                for (let i = 0; i < coordsArr.length; i++) {
                    //console.log(Object.values(coordsArr[i]));
                    placemarks.push(
                        new ymaps.Placemark(Object.values(coordsArr[i])[0], {
                            hintContent: Object.keys(coordsArr[i])[0],
                            balloonContent: key + "->" + innerKey
                        },{
                            preset: 'islands#governmentCircleIcon',
                            iconColor: color
                        })
                    );

                    // obj[key] = {
                    //     [innerKey]: Object.values(coordsArr[i])[0]
                    // };
                    //console.log(Object.keys(coordsArr[i])[0]);
                };
                // diffPts.push(obj);
                j++;
            };
            for (var i = 0; i < placemarks.length;i++) {
                placemarks[i].events.add(['click'
                    // 'mapchange', 'geometrychange', 'pixelgeometrychange', 'optionschange', 'propertieschange',
                    // 'balloonopen', 'balloonclose', 'hintopen', 'hintclose', 'dragstart', 'dragend'
                ], removePlacemark);
                myMap.geoObjects.add(placemarks[i]);
            };
        }

        //placemarks[0].geometry.getCoordinates()

        // for (let i = 0; i < diffPtsArr.length; i++) {
        //     let elem = diffPtsArr[i]
        //     for (let j = 0; j < diffPtsArr[].length; i++) {

        //     }
        // }
/////////
  //       let multiRoute = new ymaps.multiRouter.MultiRoute({   
		//     // Точки маршрута. Точки могут быть заданы как координатами, так и адресом. 
		//     // referencePoints: [
		//     //     'Москва, метро Смоленская',
		//     //     'Москва, метро Арбатская',
		//     //     [55.734876, 37.59308], // улица Льва Толстого.
		//     // ]
		//     referencePoints: ptsData["refPts"],
		//     params: {
  //               //Тип маршрутизации - пешеходная маршрутизация.
  //               routingMode: 'pedestrian'
  //               // routingMode: 'bycicile'
  //               // FIXME: Yandex Maps API can not create route on roads that exists on map!!!
  //           }
		// }, {
		//     boundsAutoApply: true
		// });

  //       myMap.geoObjects.add(multiRoute);
    }

    function removePlacemark(e) {
        for (let j = 0; j < diffPts.length; j++) {
            let coords_arr = Object.values(Object.values(diffPts[j])[0]);
            let coords_cnt = Object.values(Object.values(diffPts[j])[0]).length
            for (var i = 0; i < coords_cnt; i++) {
                if (Object.values(coords_arr[i])[0] === e.originalEvent.target.geometry.getCoordinates()) {
                    console.log(coords_arr[i]);
                    console.log(e.originalEvent.target.geometry.getCoordinates());
                    // TODO: remove point if it was clicked and its coordinates found in diffPts array
                    // OR remove point by clicking close on baloon?
                }
            }
        }
    }
    async function load_pts() {
	    let resp = await fetch('get_pts', {method: 'GET'});
	    let pts_data = await resp.json();
        if (pts_data['diff_pts']) {
            var diff_pts = pts_data['diff_pts'];
        }
        let ref_pts = pts_data['ref_pts'];


	    return {"refPts": ref_pts, "diffPts": diff_pts};
	};

    function savePoints() {
        localStorage.setItem('diffPts', JSON.stringify(placemarks));
    }


// });