# echoPal.py = serves as the main Streamlit app for EchoPal, handling user authentication, displaying role-based interfaces for
# admins and users,managing chat interactions, retrieving context from a vector database, and generating AI responses.

import streamlit as st
import interface
from response_generator import generate_response
from login import login_page, logout_button
from admin_interface import admin_interface
from embedding_manager import EmbeddingManager
# from rag_evaluator import evaluate_retrieval

# --- Authentication check ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- If not logged in, show login page ---
if not st.session_state["authenticated"]:
    login_page()

# --- If logged in, show corresponding interface ---
else:
    logout_button()  # Sidebar logout
    role = st.session_state.get("role")

    if role == "admin":
        admin_interface()

    elif role == "user":
        interface.title()

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Initialize the embedding manager (vector DB)
        if "manager" not in st.session_state:
            st.session_state.manager = EmbeddingManager()
        manager = st.session_state.manager

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Ask EchoPal something"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            print("🔍 Starting vector search for:", prompt)

            # --- Step 1: Retrieve relevant chunks from vector DB ---
            relevant_chunks = manager.search(prompt, top_k=4)  # returns list of (chunk, source)

            # *** Step 1.5: Evaluate Retrieval Performance (for Debugging purpose)
            # You’ll need to provide the ground truth manually (for evaluation runs only)
            # ground_truth_text = """
            # Part A: Cloud Governance A financial institution should ensure robust cloud governance processes are established prior to cloud adoption and are subject to on-going review and continuous improvement. This should cover the following areas: 1. Cloud risk management (a) The board of a financial institution should promote and implement sound governance principles throughout the cloud service lifecycle in line with the financial institution’s risk appetite to ensure safety and soundness of the financial institution. (b) The senior management of a financial institution should develop and implement a cloud risk management framework that integrates with existing outsourcing risk management framework, technology risk management framework (TRMF) and cyber resilience framework (CRF), for the board’s approval, proportionate to the materiality of cloud adoption in its business strategy, to assist in the identification, monitoring and mitigating of risks arising from cloud adoption. (c) Common cloud service models22 are Software-as-a-Service (SaaS), Platform-as-a-Service (PaaS), and Infrastructure-as-a-Service (IaaS), wherein each presents a different set of capabilities offered to the financial institution as thecloud consumer, and hence a different set of shared responsibilities. In view of this, the cloud risk management framework of the financial institution should : i) be an integral part of the financial institution’s enterprise risk management framework (ERM); ii) be tailored to the cloud service models, both currently in use or being considered for use; and iii) specify the scope of the financial institution’s responsibility under each shared responsibility model, as the associated risks may vary. (d) A financial institution is responsible for the protection of data stored in cloud irrespective of cloud service models and the cloud service providers. Therefore, the financial institution’s understanding of the specific details of the cloud arrangement, particularly what is or is not specified in the terms of the contract with the cloud service providers is essential. (e) Regardless of the cloud arrangement with cloud service providers, the onus remains on the financial institution to satisfy the Bank that it is protecting customer information and ensuring service reliability.(f) The use of cloud services may represent a paradigm shift in technology operation management as compared to on-premises IT infrastructure. Business processes may change and internal controls on compliance, business continuity, information and data security may be overlooked due to the ease of subscribing to cloud services. Therefore, the cloud risk management framework should also clearly articulate the accountability of the financial institution’s board and senior management and the process involved in approving and managing cloud service usage, including the responsibility of key functions across the enterprise in business, IT, finance, legal, compliance and audit, over the lifecycle of cloud service adoption. (g) As the cloud landscape rapidly evolves, a financial institutions cloud risk management framework should undergo periodic review (at least once every three years to ensure its adequacy and effectiveness to manage new service models over time), or immediately upon any major cyber security incidents involving the cloud services. 2. Cloud usage policy (a) The financial institution’s senior management should develop and implement internal policies and procedures that articulate the criteria for permitting or prohibiting the hosting of information assets on cloud services, commensurate with the level of criticality of the information asset and the capabilities of the financial institution to effectively manage the risks associated with the cloud arrangement. (b) A financial institution should expand the scope of its current technology assets inventory to include critical systems hosted on the cloud services, with a clear assignment of ownership, and to be updated upon deployment and changes of IT assets to facilitate timely recalibration of cybersecurity posture in tandem with an evolving threat landscape. Having visibility on the latest view of the technology asset would enable effective triaging, escalation and response to information security incidents. (c) A financial institution should regularly review and update the cloud usage policy at least once every three years. However, where any material changes arise, including but not limited to adoption of new cloud service deployment model, or adoption of cloud service for IT systems with higher degree of criticality, the financial institution should review and update its cloud usage policy immediately. 3. Due diligence4. Access to cloud service providers’ certifications A financial institution should review their cloud service providers’ certifications prior to entering into any cloud arrangement or contract with such cloud service providers. At a minimum, a financial institution should: (a) Seek assurance that the cloud service provider continues to be compliant with relevant legal, or regulatory requirements as well as contractual obligations and assess the cloud service provider’s action plans for mitigating any non-compliance; and (b) Obtain and refer to credible independent external party reports of the cloud platforms when conducting risk assessments. The financial institution’s risk assessment should address all the requirements and guidance as stipulated in the Cloud Services section (paragraphs 10.49 to 10.51) of this policy document and paragraph 11 of the Bank’s policy document on Outsourcing which sets out provisions on outsourcing involving cloud services. 5. Contract management A financial institution should set out clearly and where relevant, measurable, contractually agreed terms and parameters on the information security and operational standards expected of the cloud service providers. Such contract terms and parameters should be aligned with the financial institution’s business strategy, information security policies and regulatory requirements. (a) The terms of the contracts between the financial institution and cloud service providers should address the risks associated with cloud services and third party service providers as stipulated in the Cloud Services section (paragraphs 10.49 to 10.51) of this policy document and related paragraphs in the Bank’s Outsourcing policy document (Outsourcing agreement – paragraphs 9.6 and 9.7, and Protection of data confidentiality – paragraphs 9.8 and 9.9); (b) Jurisdiction risk may arise because cloud service providers operate regionally or globally in nature and may be subject to the laws and regulatory requirements of its home country, the location of incorporation, and the country where the client receives the service. Therefore, a financial institution should: i) identify and address potential jurisdiction risks by adopting appropriate mitigating measures, where practically possible, to ensure the use of cloud services does not impair its ability to comply with local law and regulatory requirements; and ii) understand the scope of local customer protection legislation and regulatory requirements as well as to ensure that the financial institution receives adequate protection and recourse for the benefit of its customers, in the event of a data breach or fulfilment of a legal data request by the cloud service provider; (c) A financial institution should assess the potential impact and formalise arrangements with cloud service providers to comply with local laws and regulatory requirements for incident investigation and law enforcement purposes. This would include adhering to data retention requirements and data access procedural arrangements to ensure the confidentiality and privacy of the customers are protected; and (d) The provision of cloud services by the primary cloud service provider may interconnect with multiple layers of other fourth party service providers (such as sub-contractors), which could change rapidly. For example, customer data could be leaked due to exposure caused by fourth party service providers. To mitigate the risks associated with such fourth party service providers, financial institutions should: i) understand the scope of customer information shared across the supply chain and ensure that relevant information security controls can be legally enforced by the financial institution; and ii) ensure Service Level Agreement (SLA) negotiations and contractual terms cover the performance matrix, availability, and reliability of services in order to ensure that the cloud service providers agree and are formally aligned on the requirements and standard of cloud services provided. In addition, cloud service providers should be accountable to the financial institution for the SLA, performance matrix, availability and reliability of cloud services rendered by its service providers (i.e. subcontractors). 6. Oversight over cloud service providers A financial institution should ensure effective oversight over cloud service providers taking into account the fact that the cloud service providers may engage sub-contractor(s) to provide cloud services. This includes, at a minimum, the following: (a) establish and define a continuous monitoring mechanism with alignment to the enterprise outsourcing risk management framework (or equivalent) to ensure adherence to the agreed SLA, compliance of the cloud service provider with any applicable legal and regulatory requirements and resilience of outsourced technology services on on-going basis; (b) identify, assign and document the key responsibilities within the financial institution for continuous monitoring of cloud service providers to ensure accountabilities are clearly defined; (c) perform assessments of the outsourcing arrangement involving cloud service providers periodically in accordance with the financial institution’s internal policy to achieve business resilience with emphasis on data security and ensure prompt notification to the Bank of the developments that may result in material impact to the financial institution (such as jurisdiction risks for data hosted overseas due to evolving foreign legislation and geopolitical development) in line with the Bank’s policy document on Outsourcing (Outsourcing PD), in particular, provisions relating to outsourcing of cloud services outside Malaysia including paragraphs 9, 10 and 11 of the Outsourcing PD; and (d) promptly review or re-perform risk assessment upon any material changes in cloud risk profile such as jurisdiction risks for data hosted overseas due to evolving foreign legislation and geopolitical development. 7. Skilled personnel with knowledge on cloud services (a) The adoption of cloud services require commensurate changes to the financial institution’s internal resources and process capabilities. In this regard, a financial institution should: i) equip its board and senior management with appropriate knowledge to conduct effective oversight over the cloud adoption; and ii) ensure its IT and security operations or relevant personnel are appropriately skilled in the areas of cloud design, migration, security configurations, including administrative, monitoring and incident response; (b) The effective management of cloud services is not purely the responsibility of the financial institutions’ IT function. Therefore, a financial institution should ensure relevant internal resources in business operations, finance, procurement, legal, risk and compliance are also adequately skilled and engaged to manage the change in risk profile arising from cloud adoption. This should also enable financial institutions to respond effectively to operational incidents; (c) A financial institution should equip internal audit and personnel undertaking the risk management and compliance functions with relevant cloud computing and cloud security skills to be able to verify the effectiveness of the information security controls in alignment with the financial institution’s cloud usage policy and information security objectives; (d) A financial institution should ensure that its staff receive adequate training to understand their responsibilities in complying with internal cloud usage policies and are prepared to effectively respond to a range of security incident scenarios developed on a risk-based approach; and (e) A financial institution should expand the scope of the formal consequence management process to govern the use of cloud services to ensure the cloud usage policy is effectively enforced given that cyber hygiene is critical to ensure the continued security of cloud service usage."""
            # # Collect all chunks from your collection for evaluation
            # all_docs = [doc for doc, _, _ in relevant_chunks]  # or fetch from your embedding manager if available
            #
            # # Extract only chunk texts
            # retrieved_texts = [doc for doc, _, _ in relevant_chunks]
            #
            # # Run evaluation
            # metrics = evaluate_retrieval(ground_truth_text, retrieved_texts, all_docs, threshold = 0.7)
            # st.write(
            #     f"📊 **Recall:** {metrics['recall']:.2f} | **Precision:** {metrics['precision']:.2f} | **F1:** {metrics['f1']:.2f}")
            # (for Debugging purpose) ***

            # --- Step 2: Inspect and log distances ---
            print("🧠 Retrieved chunks with distances:")
            for doc, src, dist in relevant_chunks:
                print(f"   → Distance: {dist:.3f} | Source: {src}")

            # --- Step 3: Adaptive filtering ---
            filtered = [(doc, src, dist) for doc, src, dist in relevant_chunks if dist < 0.25] # ori < 0.6

            if not filtered:
                print("⚠️ No chunks below threshold. Using best match as fallback.")
                if relevant_chunks:
                    filtered = relevant_chunks[:1]  # fallback to best match

            # --- Step 4: Generate response ---
            if not filtered:
                response = "Apologies, I don’t have the answer for it."
                sources_used = []
            else:
                context_text = "\n\n".join([f"From {src}: {doc}" for doc, src, dist in filtered])
                # Collect unique sources for citation display
                sources_used = list({src for _, src, _ in filtered})

                guarded_prompt = (
                    "You are EchoPal, a policy assistant for a bank. "
                    "Answer the user's question *only* using the information in the context below. "
                    "Provide a **complete and well-explained answer**, covering all relevant reasons and implications mentioned in the context."
                    "If the answer cannot be found in the context, reply exactly: "
                    "'Apologies, I couldn't answer your query as it is outside my knowledge base.'\n\n"
                    f"Context:\n{context_text}\n\n"
                    f"Question: {prompt}\n\nAnswer:"
                )

                response = generate_response(guarded_prompt)

            # --- Step 5: Display response ---
            with st.chat_message("assistant"):
                st.markdown(response)

                # ✅ Add a visible citation section
                if sources_used:
                    sources_list = ", ".join(sources_used)
                    st.markdown(f"**📚 Sources:** {sources_list}")

            st.session_state.messages.append({"role": "assistant", "content": response})
            # # --- Step 2: Prepare context for model ---
            # # context_text = "\n".join(relevant_chunks)
            #
            # # --- Step 2: Grounding logic — ensure relevant info is found
            # # Filter out weak matches
            # filtered = [(doc, src, dist) for doc, src, dist in relevant_chunks if dist < 0.7]
            #
            # if not filtered:
            #     response = "Apologies, I dont have the answer for it"
            # else:
            #     # use only filtered chunks
            #     context_text = "\n\n".join([f"From {src}: {doc}" for doc, src, dist in filtered])
            #
            #     # generate response with grounded context
            #     guarded_prompt = (
            #         "You are EchoPal, a policy assistant for a bank. "
            #         "Answer the user's question *only* using the information in the context below. "
            #         "If the answer cannot be found in the context, reply exactly: "
            #         "'Apologies, I couldn't answer your query as it is outside my knowledge base.'\n\n"
            #         f"Context:\n{context_text}\n\n"
            #         f"Question: {prompt}\n\nAnswer:"
            #     )
            #
            #     response = generate_response(guarded_prompt)
            #
            # # Display response
            # with st.chat_message("assistant"):
            #     st.markdown(response)
            #
            # st.session_state.messages.append({"role": "assistant", "content": response})
