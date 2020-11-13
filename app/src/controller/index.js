/*
 * # **********************************************************************
 * # Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
 * #
 * # All Rights Reserved.
 * # For any other permission, please contact the Legal Office at JHU/APL.
 *
 * # Licensed under the Apache License, Version 2.0 (the "License");
 * # you may not use this file except in compliance with the License.
 * # You may obtain a copy of the License at
 *
 * #    http://www.apache.org/licenses/LICENSE-2.0
 *
 * # Unless required by applicable law or agreed to in writing, software
 * # distributed under the License is distributed on an "AS IS" BASIS,
 * # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * # See the License for the specific language governing permissions and
 * # limitations under the License.
 * # **********************************************************************
 */
 import moment from 'moment'
var momentDurationFormatSetup = require("moment-duration-format");

export function mapArrayToObject(arr) {
  const new_arr = arr.map(x => {
    return x
  });
  return new_arr
}

export function mapArrObjToArr(arr_obj) {
  const new_arr = arr_obj.map(x => {
    return x
  });
  return new_arr
}
export function convert_seconds(seconds){
	momentDurationFormatSetup(moment);
	return moment.duration(seconds, "second").format("h:m:s.S", {trim:false})
	// return moment.duration(seconds, "second").format("h [h], mm [m], ss.SS [s]", { trim: false })
}
export function filterEntriesTable(row, filter, tablekey, filterOn){
  let count =0
  const keys = Object.keys(row).filter((d)=>{
    if (filterOn.length > 0 ){
      return filterOn.includes(d)
    } else { return true}
  }) 
  for (var i = 0; i < filter.length; i++){
    const string = filter[i].toUpperCase()
    for (let j =0; j < keys.length; j++){
      const key = row[keys[j]].toString().toUpperCase()
      if ((filter.length ==1 && (string =="" || !string )) ||  key.includes(string)){
        count+=1;
        break;
      }   
    }         
  }
  if (tablekey =='and'){
    if (count == filter.length){
      return true
    } else{
      return false
    }
  } else{
    if (count > 0){
      return true
    } else{
      return false
    }
  }
}

