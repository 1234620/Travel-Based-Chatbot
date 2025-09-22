"use client"

import type * as React from "react"
import { ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from "lucide-react"
import { DayPicker } from "react-day-picker"

import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"
import { Button } from "@/components/ui/button"

export type CalendarProps = React.ComponentProps<typeof DayPicker>

function Calendar({ className, classNames, showOutsideDays = true, ...props }: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-4 bg-white rounded-lg shadow-lg border", className)}
      classNames={{
        months: "flex flex-col sm:flex-row space-y-4 sm:space-x-4 sm:space-y-0",
        month: "space-y-4",
        caption: "flex justify-between items-center pt-1 pb-2",
        caption_label: "text-sm font-medium flex items-center gap-1 cursor-pointer hover:text-primary",
        nav: "flex items-center gap-1",
        nav_button: cn(
          buttonVariants({ variant: "ghost" }),
          "h-6 w-6 bg-transparent p-0 opacity-70 hover:opacity-100 hover:bg-accent",
        ),
        nav_button_previous: "",
        nav_button_next: "",
        table: "w-full border-collapse",
        head_row: "grid grid-cols-7 gap-0 mb-2",
        head_cell: "text-muted-foreground w-8 h-8 font-medium text-xs flex items-center justify-center",
        row: "grid grid-cols-7 gap-0",
        cell: "h-8 w-8 text-center text-sm p-0 relative hover:bg-accent/50 rounded-sm",
        day: cn(
          "h-8 w-8 p-0 font-normal text-sm hover:bg-accent hover:text-accent-foreground rounded-sm transition-colors",
          "focus:bg-accent focus:text-accent-foreground focus:outline-none",
        ),
        day_range_end: "day-range-end",
        day_selected:
          "bg-blue-600 text-white hover:bg-blue-700 hover:text-white focus:bg-blue-600 focus:text-white rounded-sm",
        day_today: "bg-accent text-accent-foreground font-semibold",
        day_outside: "day-outside text-muted-foreground/50 opacity-50",
        day_disabled: "text-muted-foreground/30 opacity-30",
        day_range_middle: "aria-selected:bg-accent aria-selected:text-accent-foreground",
        day_hidden: "invisible",
        ...classNames,
      }}
      components={{
        IconLeft: ({ ...props }) => <ChevronLeft className="h-3 w-3" />,
        IconRight: ({ ...props }) => <ChevronRight className="h-3 w-3" />,
        Caption: ({ displayMonth }) => (
          <div className="flex justify-between items-center w-full">
            <div className="flex items-center gap-1 cursor-pointer hover:text-primary">
              <span className="text-sm font-medium">
                {displayMonth.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
              </span>
              <ChevronDown className="h-3 w-3" />
            </div>
            <div className="flex items-center gap-1">
              <ChevronUp className="h-3 w-3 opacity-70 hover:opacity-100 cursor-pointer" />
              <ChevronDown className="h-3 w-3 opacity-70 hover:opacity-100 cursor-pointer" />
            </div>
          </div>
        ),
      }}
      {...props}
      footer={
        <div className="flex justify-between items-center pt-3 border-t mt-3">
          <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700 p-0 h-auto font-normal">
            Clear
          </Button>
          <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700 p-0 h-auto font-normal">
            Today
          </Button>
        </div>
      }
    />
  )
}
Calendar.displayName = "Calendar"

export { Calendar }
