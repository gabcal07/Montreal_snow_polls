import React, { useEffect, useState } from 'react';
import './app.css'


class Plan {
  name: string;
  snowplows1: number;
  snowplows2: number;
  distance_deneigeuse1: number;
  distance_deneigeuse2: number;
  distance_drone: number;
  duration_string : string;
  duration: number;
  duration_drone: number;
  duration_drone_string : string;

  constructor(name : string, snowplows1 : number, snowplows2 : number, distance_deneigeuse1 : number, distance_deneigeuse2 : number, distance_drone : number, duration : number, duration_drone : number)
  {
    this.name = name;
    this.snowplows1 = snowplows1;
    this.snowplows2 = snowplows2;
    this.distance_deneigeuse1 = distance_deneigeuse1;
    this.distance_deneigeuse2 = distance_deneigeuse2;
    this.distance_drone = distance_drone;
    let h = 0;
    let m = 0;
    if (duration > 60)
      {
        h = Math.floor(duration/60);
        m = duration%60;
      }
      else
      {
        m = duration;
      }
    this.duration = 2*h;
    this.duration_string = 2*h+'h'+m;
    if (duration_drone > 60)
      {
        h = Math.floor(duration_drone/60);
        m = duration_drone%60;
      }
      else
      {
        m = duration_drone;
      }
    this.duration_drone_string = h+'h'+m;
    this.duration_drone = h;


    
  }


  calculatePrice()
  {
    let c1 = this.snowplows1 * (500*this.duration/24 + (1.1*(this.distance_deneigeuse1 + this.duration < 8 ? this.duration : 8)) + 1.3*(this.duration>8 ? this.duration-8 : 0));
    let c2 = this.snowplows2 * (800*this.duration/24 + (1.3*(this.distance_deneigeuse2 + this.duration < 8 ? this.duration : 8)) + 1.5*(this.duration>8 ? this.duration-8 : 0));
    let ce = 32 * this.duration * (this.snowplows1+this.snowplows2) * 1.5;
    let cd = 0.1 * this.distance_drone * Math.ceil(this.duration_drone / 24);
    return Math.ceil(c1 + c2 + ce + cd);
  }

  calculateScore(datas)
  {
    let price = this.calculatePrice();
    return price * 0.4 / datas[0] + this.duration * 0.3 / datas[1] + (this.distance_deneigeuse1+this.distance_deneigeuse2) * 0.3 / datas[2];
  }
}


const Princing = ({plan, datas} ) => {
  console.log(plan.distance_deneigeuse1)
  console.log(plan.distance_deneigeuse2)
  return (
    <div className={'princing'}>
      <div className={'princing-header'}>
        <text className={'princing-offer-title'}>{plan.name}</text>
        <text className={'princing-offer-price'}>{'$'+plan.calculatePrice()}</text>
      </div>

      <ul className={'pricing-feature-list'}>
          <li key={0} className={'princing-feature-text'}>{plan.distance_deneigeuse1+plan.distance_deneigeuse2}km</li>
          <li key={1} className={'princing-feature-text'}>{plan.snowplows1+" déneigeuses I"}</li>
          <li key={2} className={'princing-feature-text'}>{plan.snowplows2+" déneigeuses II"}</li>
          <li key={3} className={'princing-feature-text'}>{plan.duration_string}</li>
          <li key={4} className={'princing-feature-text'}>Score: {Math.round(100000*1/Math.round(plan.calculateScore(datas))*1000)/1000}</li>

      </ul>
    </div>
  );
};



export function App() {

  const defaultTab = 'Anjou';
  const [activeTab, setActiveTab] = useState(defaultTab);

  const TabList = ({ tabs, defaultTab }) => {

    const handleTabClick = (tab) => {
      setActiveTab(tab);
    };

    return (
      <>
        <div className="tab-container">
          {tabs.map(tab => 
          {
            if (tab === activeTab)
              {
                return (
                  <div
                    key={tab}
                    className={'tab-box-active'}
                  >
                <text className={'tab-box-text'}>{tab}</text>
                  </div>
                )
              }
            return (
              <div
                key={tab}
                className={'tab-box'}
                onClick={() => handleTabClick(tab)}
              >
                <text className={'tab-box-text'}>{tab}</text>
              </div>
            )
          }
          )}
        </div>
      </>
    );
  };



  const tabs = ['Anjou', 'LPMR', 'Outremont', 'RPPT', 'Verdun'];
  const quartier_data: { [key: string]: number[] } = {
    Anjou: [3500000, 8, 100],
    LPMR: [2500000, 6.5, 169],
    Outremont: [1000000,2.66, 74],
    RPPT: [10600000, 25.33, 718],
    Verdun: [1500000, 4, 101],
  };
  const [activePricing, setPricingPlans] = useState([]);
const [drone, setDrone] = useState("");

const DroneButton = ({drone_}) => 
  { 
    if (drone_ === "-drone")
    {
      return (
        <button className={"drone-button"} onClick={() => setDrone("")}>
          <text className={"tab-box-text"}>
            Voir Déneigeuses
          </text>
        </button>
      )
    }
    return (
      <button className={"drone-button"} onClick={() => setDrone("-drone")}
      >
        <text className={"tab-box-text"}>
          Voir Drone
        </text>
      </button>
    )  
  }
  useEffect(() => {
    fetch(`/${activeTab}.json`)
      .then(response => response.json())
      .then(data =>   
            {
              console.log(data)
              const planObjects = data.pricingPlans.map(planData =>
                new Plan(
                  planData.name,
                  planData.snowplows1,
                  planData.snowplows2,
                  planData.distance_deneigeuse1,
                  planData.distance_deneigeuse2,
                  planData.distance_drone,
                  planData.duration,
                  planData.duration_drone
                )
              );
              setPricingPlans(planObjects);
            })
      .catch(error => console.error('Error loading JSON:', error));
  }, [activeTab]);



  return (
    <div className='all'>
      <h1>ERO1</h1>
        <div className={"map-tab"}>
          <div className={'tab'}>
            <iframe id="map" width="800" height={500} src={`/${activeTab}-animation${drone}.html`}></iframe>
          </div>
          <div className={'tab'}>
            <TabList tabs={tabs} defaultTab={tabs[0]} />
          </div>
          <div className={"tab"}>
            <DroneButton drone_={drone} />
          </div>
         
        </div>
      {drone == "" && 
        <><h1>Scénarios</h1> <div className={'pricings'}>  
        {
          activePricing.map((pricingPlan, index) => 
            {
                return < Princing key={index} plan={pricingPlan} datas={quartier_data[activeTab]}/>
            })
        }
        </div></>
      }
        
    </div>
  )
}
