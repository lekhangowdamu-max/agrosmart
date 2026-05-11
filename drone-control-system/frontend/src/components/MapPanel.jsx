import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const droneIcon = new L.Icon({
  iconUrl: "https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-green.png",
  iconSize: [28, 44],
  iconAnchor: [14, 44],
  popupAnchor: [0, -36],
});

const waypointIcon = new L.Icon({
  iconUrl: "https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-orange.png",
  iconSize: [28, 44],
  iconAnchor: [14, 44],
  popupAnchor: [0, -36],
});

const MapEvents = ({ onWaypoint }) => {
  useMapEvents({
    click(e) {
      onWaypoint({ latitude: e.latlng.lat, longitude: e.latlng.lng });
    },
  });
  return null;
};

const MapPanel = ({ telemetry, onWaypoint }) => {
  const [position, setPosition] = useState([26.9124, 75.7873]);

  useEffect(() => {
    if (!telemetry) return;
    setPosition([telemetry.latitude, telemetry.longitude]);
  }, [telemetry]);

  return (
    <div className="rounded-3xl border border-slate-700/70 bg-slate-950/85 p-5 shadow-drone backdrop-blur-xl">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-400/75">Map</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Farm field overview</h3>
        </div>
        <span className="rounded-full bg-slate-800/70 px-3 py-1 text-xs uppercase tracking-[0.3em] text-slate-300">Waypoint</span>
      </div>

      <div className="h-[520px] rounded-3xl overflow-hidden border border-slate-800/80">
        <MapContainer center={position} zoom={15} scrollWheelZoom={true} className="h-full w-full">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Marker position={position} icon={droneIcon}>
            <Popup>
              Drone position<br />{telemetry?.latitude?.toFixed(5)}, {telemetry?.longitude?.toFixed(5)}
            </Popup>
          </Marker>
          {telemetry?.waypoint && (
            <Marker position={[telemetry.waypoint.latitude, telemetry.waypoint.longitude]} icon={waypointIcon}>
              <Popup>Selected waypoint</Popup>
            </Marker>
          )}
          <MapEvents onWaypoint={onWaypoint} />
        </MapContainer>
      </div>

      <p className="mt-4 text-sm text-slate-400">Click anywhere on the map to set a new waypoint for the drone.</p>
    </div>
  );
};

export default MapPanel;
