from gotrue.types import UserResponse
from postgrest.base_request_builder import APIResponse
import streamlit, datetime, json
from typing import Any, Dict
from supabase import create_client
from streamlit.delta_generator import DeltaGenerator
from supabase._sync.client import SyncClient


def intro_tab_function() -> None:
    #-------------------------------------------------------
    # Link to Database
    #-------------------------------------------------------
    
    try:
        supabase_url: str = streamlit.secrets["connections"]["supabase"]["SUPABASE_URL"]
        supabase_key: str = streamlit.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        
        supabase: SyncClient|None = create_client(supabase_url, supabase_key)
        supabase_available = True
    except:
        supabase: SyncClient|None = None
        supabase_available = False

    #-------------------------------------------------------
    # Miscellaneous functions
    #-------------------------------------------------------
    def apply_date_formatting(date: datetime.date) -> str:
        reformatted_date: str = date.strftime("%b %Y")
        return reformatted_date
    
    def apply_time_duration_formating_for_job_roles(start_date_of_role: datetime.date, end_date_of_role: datetime.date) -> str:
        """
        Applies the date formatting viewable below the job title.\n
        ***Examples:***\n
        - "May 2025 - (<1 month)"
        - "Apr 2025 to May 2025 - (1 month)"
        - "Nov 2024 to May 2025 - (6 months)"
        - "May 2024 to May 2025 - (1 year)"
        - "Apr 2024 to May 2025 - (1 year 1 month)"
        - "Mar 2024 to May 2025 - (1 year 2 months)"
        - "May 2023 to May 2025 - (2 years)"
        - "Apr 2023 to May 2025 - (2 years 1 month)"
        - "Mar 2023 to May 2025 - (2 years 2 months)"
`        """
        if end_date_of_role == datetime.date.today(): # Current role
            role_duration_in_months: int = round((end_date_of_role - start_date_of_role).days/ 30.436875)
            if role_duration_in_months < 12: # less than 1 year in
                if role_duration_in_months == 0:  # just started
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to Present* :grey[- *(<1 month)*]]"
                elif role_duration_in_months == 1: # 1 month in
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to Present*]  :grey[- *({role_duration_in_months} month)*]"
                else:
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to Present*]  :grey[- *({role_duration_in_months} months)*]"
            elif role_duration_in_months == 12: # 1 year in
                reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to Present*]  :grey[- *(1 year)*]"
            else: # greater than 1 year in
                role_duration_years: int = int(role_duration_in_months / 12)
                if role_duration_years > 1:
                    years_plural_or_not = "years"
                else:
                    years_plural_or_not = "year"
                remaining_of_role_duration_in_months: int = role_duration_in_months - (int(role_duration_years * 12))
                if remaining_of_role_duration_in_months > 1:
                    months_plural_or_not: str = "months"
                    remove_months: bool = False
                elif remaining_of_role_duration_in_months == 0:
                    months_plural_or_not: str = ""
                    remove_months: bool = True
                else:
                    months_plural_or_not: str = "month"
                    remove_months: bool = False
                if remove_months:
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to Pesent*]  :grey[- *({role_duration_years} {years_plural_or_not})*]"
                else:
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to Pesent*]  :grey[- *({role_duration_years} {years_plural_or_not} {remaining_of_role_duration_in_months} {months_plural_or_not})*]"
        else: # Past role
            role_duration_in_months: int = round((end_date_of_role - start_date_of_role).days/ 30.436875)
            if role_duration_in_months < 12: # Less than 1 year
                if role_duration_in_months == 0:  # less than 1 month -- If I was superhero for a week, you can bet it'll be on my resume!
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)}*] :grey[- *(<1 month)*]"
                elif role_duration_in_months == 1: # 1 month
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to {apply_date_formatting(end_date_of_role)}*]  :grey[- *({role_duration_in_months} month)*]"
                else: # more than 1 month but less than a full year
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to {apply_date_formatting(end_date_of_role)}*]  :grey[- *({role_duration_in_months} months)*]"
            elif role_duration_in_months == 12: # 1 year
                reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to {apply_date_formatting(end_date_of_role)}*]  :grey[- *(1 year)*]"
            else: # More than 1 year
                role_duration_years: int = int(role_duration_in_months / 12)
                if role_duration_years > 1:
                    years_plural_or_not = "years"
                else:
                    years_plural_or_not = "year"
                remaining_of_role_duration_in_months: int = role_duration_in_months - (int(role_duration_years * 12))
                if remaining_of_role_duration_in_months > 1:
                    months_plural_or_not: str = "months"
                    remove_months: bool = False
                elif remaining_of_role_duration_in_months == 0:
                    months_plural_or_not: str = ""
                    remove_months: bool = True
                else:
                    months_plural_or_not: str = "month"
                    remove_months: bool = False
                if remove_months:
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to {apply_date_formatting(end_date_of_role)}*]  :grey[- *({role_duration_years} {years_plural_or_not})*]"
                else:    
                    reformatted_role_duration: str = f":blue[*{apply_date_formatting(start_date_of_role)} to {apply_date_formatting(end_date_of_role)}*]  :grey[- *({role_duration_years} {years_plural_or_not} {remaining_of_role_duration_in_months} {months_plural_or_not})*]"

        return reformatted_role_duration


    tab1, tab2, tab3, tab4 = streamlit.tabs(["Landing Page","Career Experience","Education","Certificates"])

    with tab1:
        
        tab1_container1: DeltaGenerator = streamlit.container()
        tab1_container2: DeltaGenerator = streamlit.container()

        #-------------------------------------------------------
        # Welcome message
        #-------------------------------------------------------
        tab1_container1.subheader(""":primary[Welcome to my web CV!]""", anchor=False)
        
        tab1_container1.markdown(
            """ - *I am a supply chain professsional with a passion for taking highly complex challenges and generating lasting solutions.*"""
        )
        
        tab1_container1.markdown(
            """ - *I learn very quickly and enjoy learning about new technologies and computer science.*"""
        )
        
        tab1_container1.markdown(
            """ - *I hope you enjoy this app! Please let me know if there are any features or pages I could add which would improve your experience or provide you some added utility. Your input is highly valued and appreciated.*"""
        )

        #-------------------------------------------------------
        # Download Button
        #-------------------------------------------------------
        
        # Load PDF
        with open("James_Marshall_CV.pdf", "rb") as pdf_resume:
            PDFbyte: bytes = pdf_resume.read()

        # Display download button
        tab1_container1.download_button(
            label="Click to download my resume",
            data=PDFbyte,
            file_name="James_Marshall_CV.pdf",
            mime="application/pdf"
        )

        #-------------------------------------------------------
        # User Feedback
        #-------------------------------------------------------

        tab1_container2.subheader(""":primary[How is your user experience?]""", anchor=False)

        if not supabase_available:
            tab1_container2.info("Sorry for the inconvenience, this feature is currently unavailable.")
        else:
            star_mapping: list[int] = [1,2,3,4,5]
            user_feedback_rating: int|None = tab1_container2.feedback("stars")
            prompts: tuple = (
                "Oh no! That bad? I'm so sorry. Please let me know how I can improve:",
                "Oh no! I guess I could've done worse, but I'm nowhere near where I want to be. How can I improve?",
                "Thank you for your feedback! I want to do better. Please let me know how I can improve:",
                "I'm glad you enjoyed your visit! Please let me know how I can earn that last star!",
                "I'm glad you enjoyed your visit! Maybe I can still improve?"
            )
            if user_feedback_rating is not None:
                rating: int = star_mapping[user_feedback_rating]
                feedback_text: str = str(tab1_container2.text_input(prompts[user_feedback_rating], key="feedback_input"))
                submit: bool = tab1_container2.button("Submit Feedback")
                if submit:
                    if feedback_text.strip(): # Ensure the contents are not just white-space
                        try:
                            feedback_entry: APIResponse[Dict[str, Any]] = supabase.table("feedback").insert({
                                "Creation_timestamp": datetime.datetime.now().isoformat(),
                                "Rating": rating,
                                "Feedback": feedback_text.strip()
                            }).execute()

                            tab1_container2.success("Thank you! Your feedback has been submitted. ")
                        except:
                            tab1_container2.error(f"Sorry, it's not you--it's me. There was an error when submitting your feedback.")
                    else:
                        streamlit.warning("Oops, that didn't work. Please enter your feedback and try re-submitting.")
    
    
    with tab2:

        total_years_experience_container: DeltaGenerator = streamlit.container(border=False)
        skpt_planner_2_container: DeltaGenerator = streamlit.container(border=True)
        skpt_planner_1_container: DeltaGenerator = streamlit.container(border=True)
        skpt_planner_1_container: DeltaGenerator = streamlit.container(border=True)
        avbio_analyst_container: DeltaGenerator = streamlit.container(border=True)
        avbio_clerk_container: DeltaGenerator = streamlit.container(border=True)
        kite_pharm_container: DeltaGenerator = streamlit.container(border=True)

        # Define variables for years of experience and durations of roles
        skpt_planner_2_start: datetime.date = datetime.date(2024,5,1)
        skpt_planner_2_end: datetime.date = datetime.date.today()
        skpt_planner_1_start: datetime.date = datetime.date(2021,12,1)
        skpt_planner_1_end: datetime.date = skpt_planner_2_start
        avbio_analyst_start: datetime.date = datetime.date(2021,3,1)
        avbio_analyst_end: datetime.date = datetime.date(2021,12,1)
        avbio_clerk_start: datetime.date = datetime.date(2019,9,1)
        avbio_clerk_end: datetime.date = avbio_analyst_start
        kite_pharm_start: datetime.date = datetime.date(2018,6,1)
        kite_pharm_end: datetime.date = datetime.date(2018,9,1)

        # Years of Experience = From Avidbio Clerk Start to end-date of current or most recent poosition + 3 month internship at Kite Pharma
        time_work_experience: datetime.timedelta = skpt_planner_2_end -  avbio_clerk_start
        time_internship_experience: datetime.timedelta = kite_pharm_end -  kite_pharm_start
        total_work_experience_in_days: int = time_work_experience.days + time_internship_experience.days
        total_work_experience_in_years: float = round(total_work_experience_in_days / 365.2422, 1)

        total_years_experience_container.markdown(f":blue[{rf"$\textsf{{ Total Experience: {total_work_experience_in_years} in years}}$"}]")

        #-------------------------------------------------------
        # SKPT - Planner II
        #-------------------------------------------------------
        skpt_planner_2_container.subheader(":primary[SK Pharmteco] - *E2E Business Unit Planner II*", anchor=False)
        # skpt_planner_2_container.markdown(":blue[***E2E Business Unit Planner II***]")
        skpt_planner_2_container.markdown(apply_time_duration_formating_for_job_roles(skpt_planner_2_start, skpt_planner_2_end))
        skpt_planner_2_container.markdown("""
        
        - *Supply chain lead for new product introductions (NPIs).*
        - *Coordinates end to end supply chain activities among stakeholders across various departments.*
        - *Responsible for for proactively forecasting, planning, buying, and expediting materials.*
        - *Maintains accurate MRP inputs (BOM/BOO/forecast) & mitigates or
        escalates risks when identified.*
        - *Conducts complex data analysis to identify bottlenecks, inform
        decisions, prepare for negotiations, or assess scenarios.*
        - *Facilitates materials readiness meetings with leadership & clients.*
        - *Contributes and owns Change Controls in Veeva Quality Management System (QMS) as needed*.
        - *Autonomously pursues process improvements and integration of data across software platforms.*
        - *Owns and/or contributes to change controls in Veeva quality management system as needed.*
        - *Built a web application using python-code dedicated to providing advanced
        data insights and analytics for materials planning. These analytics support: 
        buy-decisions, risk assessments, adjustments to stock-level and reorder point settings, materials-related investigations,
        historical lead time trends, identification of alternate materials, verifications of master data integrity, and more.*
        - *Iterated a self-built material planning tool which further-reduced focus-hours to plan from 26 to 14.5 hours per planner per week.*
        - *Built a template for automating and standardizing
        status-updates on materials readiness, enabling near real-time report-outs and reducing
        manual preparations by roughly 2 hours per materials readiness meeting per week.*
        - *Miscellaneous accomplishments: (1) received a spotlight award for dedication to clients; (2) identified  $1.7M of SLOB
        inventory for disposition; (3) further-automated manual routine activities via python-code to perform
        automated data-refreshes and mass-analytics by SKU which support both high-level materials oversight and SKU-level evaluations.*
                                                
        """)


        #-------------------------------------------------------
        # SKPT - Planner I
        #-------------------------------------------------------
        skpt_planner_1_container.subheader(":primary[SK Pharmteco] - *E2E Business Unit Planner I*", anchor=False)
        skpt_planner_1_container.markdown(apply_time_duration_formating_for_job_roles(skpt_planner_1_start, skpt_planner_1_end))
        skpt_planner_1_container.markdown("""
        - *Supply chain lead for new product introductions (NPIs).*
        - *Coordinates end to end supply chain activities among stakeholders across various departments.*
        - *Responsible for for proactively forecasting, planning, buying, and expediting materials.*
        - *Maintains accurate MRP inputs (BOM/BOO/forecast) & mitigates or
        escalates risks when identified.*
        - *Conducts complex data analysis to identify bottlenecks, inform
        decisions, prepare for negotiations, or assess scenarios.*
        - *Facilitates materials readiness meetings with leadership & clients.*
        - *Autonomously pursues process improvements and integration of data across software platforms.*
        - *Created a refreshable reporting template which utilizes algorithms via
        advanced excel functions. Iterations have led to immense increases to
        efficiency in hours required to plan and report on materials.*
        - *Was a pioneering lead and pivotal systems architect for SAP
        implementation of CPFR systems which provided MRP I & II capabilities
        enabling production orders, real-time materials consumption,
        cost-estimation on projected materials usage, and visibility to WIP inventory & COGS.*
        - *Created a materials planning template which reduced focus-hours to plan from 111 to 32 hours per planner per week.*
        - *Created headcount metrics for the SC planning team by defining job
        responsibilities and validating data inputs by tracking live activities. This 
        data supported leadership's decision to create 3 new positions.*
        - *Reduced planned materials orders by $8.9M, representing a 60% reduction to planned materials-orders by identifying
        excess requirements.*
        - *Miscellaneous contributions: (1) the numbering method of in-house
        made SKUs; (2) identified the need (and requested) for two new NDAs/CDAs; (3) identified $1.2M of SLOB inventory
        for disposition.*
        
        """)



        #-------------------------------------------------------
        # Avid Bio - Analyst
        #-------------------------------------------------------
        avbio_analyst_container.subheader(":primary[Avid Bioservices] - *Supply Chain Analyst*", anchor=False)
        avbio_analyst_container.markdown(apply_time_duration_formating_for_job_roles(avbio_analyst_start, avbio_analyst_end))
        avbio_analyst_container.markdown("""
        - *Supported the ERP system transfer from AX Dynamics 2012 to D365
        as a lead supply chain SME and super user. Performed end-user testing to
        identify bugs for IT, ensured compliance to user requirements, and created
        training scripts to enable operational deployment.*
        - *Pioneered the exploration of MRP I & II systems, including BOMs, routings, 
        and resources to enable planned system enhancements.*
        - *Assisted management's implementation of 5S practices and supported the
        inventory, logistics, and receiving crews ad-hoc.*
        - *Designed the process for inbound/outbound logistics between Avid &
        3PL warehouse.*
        - *Generated leadership/QA endorsement of larger-scale process enhancements and
        drove implementations through initial executions to ensure smooth deployment.*
        - *Pioneered the exploration and potential applications of Power BI software.*
        - *Created a new procedure for the use of a walk-in -20°C freezer supporting
        readiness of the new storage space & safety of personnel.*
        
        """)


        #-------------------------------------------------------
        # Avid Bio - Clerk
        #-------------------------------------------------------
        avbio_clerk_container.subheader(":primary[Avid Bioservices] - *Supply Chain Clerk*", anchor=False)
        avbio_clerk_container.markdown(apply_time_duration_formating_for_job_roles(avbio_clerk_start, avbio_clerk_end))
        avbio_clerk_container.markdown("""
        - *Issued & optimized stock for replenishment inventory.*
        - *Issued materials to MFG for core processes.*
        - *Performed general warehouse management operations such as re-optimizations of storage space and weekly sweeps/walkthroughs.*
        - *Responded to 24-hour emergency call-outs for equipment alarms or materials-requests.*
        - *Regularly investigated, cycle counted, & reconciled inventory.*
        - *Escalated ad-hoc materials shortages as needed including requirements for urgent quarantine release.*
        - *Performed manual GMP temperature monitoring activities every week.*
        - *Aided audits when documentation was requested.*
        - *Operated various forklifts as needed.*
                                       
        """)

        #-------------------------------------------------------
        # Internship
        #-------------------------------------------------------
        kite_pharm_container.subheader(":primary[Kite Pharma] - *External Manufacturing Intern*", anchor=False)
        kite_pharm_container.markdown(apply_time_duration_formating_for_job_roles(kite_pharm_start, kite_pharm_end))
        kite_pharm_container.markdown("""
        - *Served as a project manager on the external manufacturing team.*
        - *Responsible for researching capabilities of prospective partners (i.e. contract manufacturing organizations).*
        - *Wrote new 'Rules & Operations' dictating operational processes and interactions between Kite Pharma and its existing contract manufacturing organizations.*
        - *Assisted with administrative or clerical duties as needed.*
                                              
        """)


        #-------------------------------------------------------
        # For testing only
        #-------------------------------------------------------
        # todays_date: datetime.date = datetime.date.today()
        # one_week_ago: datetime.date = todays_date - datetime.timedelta(7)
        # one_month_ago: datetime.date = todays_date - datetime.timedelta(30)
        # six_months_ago: datetime.date = todays_date - datetime.timedelta(182.6211)
        # one_year_ago: datetime.date = todays_date - datetime.timedelta(365.2422)
        # one_year_one_month_ago: datetime.date = todays_date - datetime.timedelta(395.67905)
        # one_year_two_months_ago: datetime.date = todays_date - datetime.timedelta(426.1159)
        # two_years_ago: datetime.date = todays_date - datetime.timedelta(730.4844)
        # two_years_one_month_ago: datetime.date = todays_date - datetime.timedelta(760.92125)
        # two_years_two_months_ago: datetime.date = todays_date - datetime.timedelta(791.3581)
        
        # date_in_past: datetime.date = one_month_ago
        # one_week_before: datetime.date = date_in_past - datetime.timedelta(7)
        # one_month_before: datetime.date = date_in_past - datetime.timedelta(30)
        # six_months_before: datetime.date = date_in_past - datetime.timedelta(182.6211)
        # one_year_before: datetime.date = date_in_past - datetime.timedelta(365.2422)
        # one_year_one_month_before: datetime.date = date_in_past - datetime.timedelta(395.67905)
        # one_year_two_months_before: datetime.date = date_in_past - datetime.timedelta(426.1159)
        # two_years_before: datetime.date = date_in_past - datetime.timedelta(730.4844)
        # two_years_one_month_before: datetime.date = date_in_past - datetime.timedelta(760.92125)
        # two_years_two_months_before: datetime.date = date_in_past - datetime.timedelta(791.3581)
        
        
        # streamlit.subheader("To Present", anchor=False)
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_week_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_month_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(six_months_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_year_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_year_one_month_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_year_two_months_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(two_years_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(two_years_one_month_ago,todays_date))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(two_years_two_months_ago,todays_date))
        # streamlit.subheader("To Date in the past", anchor=False)
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_week_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_month_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(six_months_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_year_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_year_one_month_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(one_year_two_months_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(two_years_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(two_years_one_month_before,date_in_past))
        # streamlit.markdown(apply_time_duration_formating_for_job_roles(two_years_two_months_before,date_in_past))

    with tab3:
        University_start: datetime.date = datetime.date(2015,10,1)
        University_end: datetime.date = datetime.date(2019,6,30)
        
        tab3_container1: DeltaGenerator = streamlit.container(border=False)
        tab3_container1.subheader(":primary[University of California, Riverside]", anchor=False)
        tab3_container1.markdown(f":blue[{r"$\textsf{ Bachelor of Science, Business Administration \& Management}$"}]")
        tab3_container1.markdown(f":blue[*{apply_time_duration_formating_for_job_roles(University_start, University_end)}*]")
        tab3_container1.markdown("- Earned Distinctions: :primary[**Dean's Honor List & Chancellor's Honor List**]")
        tab3_container1.markdown("""
        - **Notable courses taken:**\n
            - *Production & Operations Management*
            - *Competitive & Strategic Analysis*
            - *Leadership Development*
            - *Advanced Topics: Management & Decision-Making*
            - *Decision Analysis & Management Science*
            - *Marketing & Distribution Management*
            - *Management Writing & Communication*
            - *Information Technology Management*
            - *Financial Evaluation & Managerial Analysis*
            - *Negotiation Fundamentals*
            - *Law & Economics*
        """)

    with tab4:
        tab4_container1: DeltaGenerator = streamlit.container(border=False)
        tab4_container1.subheader(":primary[APICS: Certified Supply Chain Professional (CSCP)]", anchor=False)
        tab4_container1.markdown("""
        - *ID: :blue[APICS2439201]*
        - *Registration ID: :blue[440404354]*
        - *Expiration Date: :blue[June 6, 2028]*
        """)
        tab4_container1.subheader(":primary[Lean Six Sigma: Yellow Belt]", anchor=False)
        tab4_container1.markdown("""
        - *Yellow Belt Certificate Number: :blue[0240600770]*
        - *Yellow Belt Expiration Date: :blue[June 23, 2026]*
        """)
        tab4_container1.subheader(":primary[Lean Six Sigma: Lean]", anchor=False)
        tab4_container1.markdown("""
        - *Lean Certificate Number: :blue[0240600831]*
        - *Lean Expiration Date: :blue[June 25, 2026]*
        """)
