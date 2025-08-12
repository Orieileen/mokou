import { useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"

type Props = {
  onGetMsg?: (msg: string) => void,
}

function Son (props: Props){
  const {onGetMsg} = props
  return <button onClick={()=>onGetMsg?.('qq')} ></button>
}

function App() {
  const inputRef = useRef(null)

  const timeRef = useRef<NodeJS.Timeout | undefined>(undefined)
  useEffect(()=>{
    timeRef.current = setInterval(()=>{
      console.log("1")
    },1000)
    return ()=>{clearInterval(timeRef.current)}
  },[])

  return (
    <>
    <Son onGetMsg={(msg)=>console.log(msg)}/>
    <div className="flex flex-col gap-2">
      <Button>click me</Button>
      <Button variant="outline">click me</Button>
      <Button variant="secondary">click me</Button>
      <Button variant="ghost">click me</Button>
      <Button variant="link">click me</Button>
    </div>
    <input ref={inputRef}></input>
    <button onClick={()=>console.log(inputRef.current)}>click me</button>
    </>
  )
}

export default App

