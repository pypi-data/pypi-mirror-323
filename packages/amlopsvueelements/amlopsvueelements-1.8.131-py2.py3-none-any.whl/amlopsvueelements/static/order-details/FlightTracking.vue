<template>
  <LMap
    v-if="valuesCalculated"
    v-show="!mapLoading || !valuesCalculated"
    ref="map"
    :zoom="zoom"
    :center="center"
    :use-global-leaflet="false"
    @ready="onMapReady"
  >
    <LTileLayer
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      layer-type="base"
      name="OpenStreetMap"
    >
    </LTileLayer>
    <div v-for="(flight, flightIndex) in flightsData" :key="flight.tail_number">
      <LMarker
        v-if="flight.departure_from"
        :lat-lng="[
          parseFloat(flight.departure_from.airport_details.latitude),
          parseFloat(flight.departure_from.airport_details.longitude)
        ]"
        :title="'Airport'"
      >
        <LPopup>
          <p>
            {{ flight.departure_from.details.registered_name }}({{
              flight.departure_from.airport_details.icao_code
            }}/{{ flight.departure_from.airport_details.iata_code }})
          </p>
          <p>Departure Airport</p>
          <div>
            <div v-if="flight.estimated_departure_at">
              Departure Time: {{ flight.estimated_departure_at }}
            </div>
          </div>
        </LPopup>
      </LMarker>
      <LMarker
        v-if="flight.arrival_to"
        :lat-lng="[
          parseFloat(flight.arrival_to.airport_details.latitude),
          parseFloat(flight.arrival_to.airport_details.longitude)
        ]"
        :icon="markerIcon"
      >
        <LPopup>
          <p>
            {{ flight.arrival_to.details.registered_name }}({{
              flight.arrival_to.airport_details.icao_code
            }}/{{ flight.arrival_to.airport_details.iata_code }})
          </p>
          <p>Arrival Airport</p>
          <div>
            <div v-if="flight.estimated_arrival_at">
              Arrival Time: {{ flight.estimated_arrival_at }}
            </div>
          </div>
        </LPopup>
      </LMarker>
      <LMarkerRotate
        v-if="flight.latLng && flight.latLng.length"
        :lat-lng="(flight.latLng[flight.latLng.length - 1] as LatLngTuple)"
        :icon="aircraftIcon"
        :rotation-angle="lastPos(flightIndex)?.heading"
      >
        <LPopup>
          <div class="mb-[0.5rem]">
            <div><b>Callsign: </b>{{ flight.callsign }}</div>
          </div>
          <div>
            <div><b>Heading: </b>{{ lastPos(flightIndex)?.heading }}°</div>
            <div>
              <b>Altitude: </b>{{ lastPos(flightIndex)?.altitude }}
              feet
            </div>
            <div>
              <b>Speed: </b>{{ lastPos(flightIndex)?.ground_speed }}
              knots
            </div>
          </div>
        </LPopup></LMarkerRotate
      >
      <LPolyline
        v-if="flight.flight_tracking"
        :lat-lngs="(flight.latLng as LatLngExpression[]) ?? []"
        color="#d46a70"
        :weight="2"
      />
      <LPolyline
        v-if="flight.flight_tracking && flight.departure_from"
        :lat-lngs="
        (flight.latLng as LatLngExpression[])
            ? [
                [
                  parseFloat(flight.departure_from.airport_details.latitude),
                  parseFloat(flight.departure_from.airport_details.longitude)
                ],
                flight.latLng![0] as LatLngExpression
              ]
            : []
        "
        color="#000000"
        dash-array="20, 10"
        dash-offset="0"
        :opacity="0.7"
      />
    </div>
  </LMap>
  <Loading v-if="mapLoading" />
</template>

<script setup lang="ts">
import { computed, type PropType, type Ref, ref, watch } from 'vue';
import { LMap, LMarker, LPolyline, LPopup, LTileLayer } from '@vue-leaflet/vue-leaflet';
import L, { type LatLngExpression, type LatLngTuple, type PointExpression } from 'leaflet';
// @ts-ignore
import { LMarkerRotate } from 'vue-leaflet-rotate-marker';
import { getImageUrl } from '@/helpers';
import Loading from '../forms/Loading.vue';
import 'leaflet/dist/leaflet.css';

import type { ITrackedFlight } from 'shared/types';

const props = defineProps({
  flights: {
    type: Object as PropType<ITrackedFlight[]>,
    default: null
  }
});
const zoom = ref(3);
let center = [0, 0] as PointExpression;
const mapLoading = ref(true);
const valuesCalculated = ref(false);
const markerIcon = L.icon({
  iconUrl: getImageUrl('assets/icons/marker-icon-2x-green.png'),
  iconSize: [25, 41],
  iconAnchor: [0, 41],
  shadowUrl: getImageUrl('assets/icons/marker-shadow.png'),
  shadowAnchor: [0, 41],
  shadowSize: [41, 41]
});
const aircraftIcon = L.icon({
  iconUrl: getImageUrl('assets/icons/plane.png'),
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  className: 'u-turn-icon'
});

const flightsData: Ref<Array<ITrackedFlight>> = computed(() => {
  const mapped = props.flights?.map((flight: ITrackedFlight) => {
    if (flight.flight_tracking) {
      const aircraftLocations = flight.flight_tracking.map((pos) => [
        parseFloat(pos.latitude),
        parseFloat(pos.longitude)
      ]);
      flight.latLng = aircraftLocations;
    }
    return flight;
  });
  return mapped;
});

const calcMaxDistance = (flights: ITrackedFlight[]) => {
  let maxLatitude = 0;
  let maxLongitude = 0;
  flights?.forEach((flight: ITrackedFlight) => {
    if (flight.departure_from && flight.arrival_to) {
      const latDistance = Math.abs(
        parseFloat(flight.departure_from.airport_details.latitude) -
          parseFloat(flight.arrival_to.airport_details.latitude)
      );
      const longDistance = Math.abs(
        parseFloat(flight.departure_from.airport_details.longitude) -
          parseFloat(flight.arrival_to.airport_details.longitude)
      );
      if (latDistance > maxLatitude) {
        maxLatitude = latDistance;
      }
      if (longDistance > maxLongitude) {
        maxLongitude = longDistance;
      }
    }
  });
  const getLongitudeZoomLevel = (longitude: number) => {
    if (longitude <= 10) return 7;
    if (longitude <= 25) return 6;
    if (longitude <= 50) return 5;
    if (longitude <= 100) return 4;
    return 3;
  };
  const getLatitudeZoomLevel = (latitude: number) => {
    if (latitude <= 1) return 8;
    if (latitude <= 2.5) return 7;
    if (latitude <= 5) return 6;
    if (latitude <= 9) return 5;
    if (latitude <= 20) return 4;
    if (latitude <= 50) return 3;
    return 2;
  };
  if (Math.max(maxLatitude, maxLongitude) > 0) {
    const latitudeZoom = getLatitudeZoomLevel(maxLatitude);
    const longitudeZoom = getLongitudeZoomLevel(maxLongitude);
    zoom.value = Math.min(latitudeZoom, longitudeZoom);
  }
};

const calcCenter = (flights: ITrackedFlight[]) => {
  const polygonCoords = [] as LatLngExpression[];
  flights?.forEach((el) => {
    if (el.departure_from) {
      polygonCoords.push([
        parseFloat(el.departure_from.airport_details.latitude),
        parseFloat(el.departure_from.airport_details.longitude)
      ]);
    }
    if (el.arrival_to) {
      polygonCoords.push([
        parseFloat(el.arrival_to.airport_details.latitude),
        parseFloat(el.arrival_to.airport_details.longitude)
      ]);
    }
  });
  const polygon = L.polygon(polygonCoords as LatLngExpression[]);
  const polyCenter = polygon.getBounds() ? { lat: 50, lng: 0 } : polygon.getBounds().getCenter();
  center = [polyCenter.lat, polyCenter.lng];
  valuesCalculated.value = true;
};

const lastPos = (index: number) =>
  props.flights[index].flight_tracking[props.flights[index].flight_tracking.length - 1];

const onMapReady = () => {
  setTimeout(function () {
    mapLoading.value = false;
    window.dispatchEvent(new Event('resize'));
  }, 2500);
};

watch(
  () => props.flights,
  (value) => {
    calcMaxDistance(value);
    calcCenter(value);
  }
);
</script>
