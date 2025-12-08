import { useContext } from "react";
import { Link } from "react-router-dom";
import { FaHome, FaMap, FaMagic, FaHistory, FaUser } from "react-icons/fa";
import { GlobalContext } from "../context/GlobalContext";

import "../styles/NavBar.css"

const NavBar = () => {
    const { HomeRoute, MapRoute, NewTripRoute, HistoryRoute, AccountRoute } = useContext(GlobalContext).routes;
    const { navState } = useContext(GlobalContext);
    return (
        <div className={navState?.active ? "nav-container active" : "nav-container"}>
            <nav className="navbar">
                <ul>
                    <li className="nav-item">
                        <Link className={navState?.home ? "active": ""} to={ HomeRoute }>
                            <FaHome />
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className={navState?.map ? "active": ""} to={ MapRoute }>
                            <FaMap />
                        </Link>
                    </li>
                    <li className="nav-item plus">
                        <Link className={navState?.new ? "active": ""} to={ NewTripRoute }>
                            <FaMagic />
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className={navState?.history ? "active": ""} to={ HistoryRoute }>
                            <FaHistory />
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className={navState?.account ? "active": ""} to={ AccountRoute }>
                            <FaUser />
                        </Link>
                    </li>
                </ul>
            </nav>
        </div>
    )
};

export { NavBar };