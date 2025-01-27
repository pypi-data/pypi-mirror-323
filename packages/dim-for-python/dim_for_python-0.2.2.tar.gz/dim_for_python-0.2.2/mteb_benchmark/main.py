import asyncio

import mteb
import numpy as np
from dim_python import vectorize_string
from mteb.encoder_interface import PromptType


class DimStringVectorization:
    def encode(
        self,
        sentences: list[str],
        task_name: str = "",
        prompt_type: PromptType | None = None,
        **kwargs,
    ) -> np.ndarray:
        """Encodes the given sentences using the encoder.
        
        Args:
            sentences: The sentences to encode.
            task_name: The name of the task.
            prompt_type: The prompt type to use.
            **kwargs: Additional arguments to pass to the encoder.
            
        Returns:
            The encoded sentences.
        """
        encoded_sentences = []
        
        loop = asyncio.get_event_loop()
        
        for sentence in sentences:
            encoded_sentences.append(
                loop.run_until_complete(run(sentence))
            )
       
        for encoded_sentence in encoded_sentences:
            print(encoded_sentence)
        
        return np.array(encoded_sentences)


async def run(sentence: str) -> list[float]:
    return await vectorize_string(
        string=sentence,
        prompts = [
            # Aspect 1: Transaction Intent
            "Identify the primary banking action requested in the text. Options: payments, transfers, card issues, fraud reports, account access, fees, etc. "
            "Format: {'transaction_intent': 'card_issue', 'confidence': 0-9}. Example: {'transaction_intent': 'card_payment_fee_charged', 'confidence': 8}",
        
            # Aspect 2: Product/Service Mention
            "Detect specific banking products/services mentioned (e.g., credit card, loan, savings account). Return NONE if unspecified. "
            "Format: {'product_mentioned': ['credit_card'], 'confidence': 7}. Example: {'product_mentioned': ['mobile_banking'], 'confidence': 6}",
        
            # Aspect 3: Urgency Detection
            "Rate urgency for resolution: 1 (routine inquiry) to 9 (critical issue needing immediate action). "
            "Format: {'urgency': 5}. Example (fraud report): {'urgency': 9}",
        
            # Aspect 4: Issue Type
            "Classify the problem type: technical_error, fee_dispute, transaction_failure, account_access, fraud, etc. "
            "Format: {'issue_type': 'transaction_failure', 'confidence': 7}. Example: {'issue_type': 'fee_dispute', 'confidence': 8}",
        
            # Aspect 5: Action Requested
            "Identify the explicit action the user wants (e.g., block card, refund, update details, explain charges). "
            "Format: {'action_requested': 'block_card', 'confidence': 9}. Example: {'action_requested': 'dispute_charge', 'confidence': 7}",
        
            # Aspect 6: Query Specificity
            "Score specificity of details from 1 (vague: 'my card isn't working') to 9 (detailed: 'Wire transfer failed with error CODE-2023'). "
            "Format: {'specificity': 4}. Example: {'specificity': 8}",
        
            # Aspect 7: Transaction Status
            "Determine if the text references: pending, completed, failed, or disputed transactions. Return NONE if irrelevant. "
            "Format: {'transaction_status': 'failed', 'confidence': 8}. Example: {'transaction_status': 'disputed', 'confidence': 7}",
        
            # Aspect 8: Fraud/Security Focus
            "Is this query security/fraud-related? 1 (no) to 9 (yes). "
            "Format: {'fraud_related': 3}. Example (stolen card): {'fraud_related': 9}",
        
            # Aspect 9: Payment Method
            "Identify payment method involved: credit/debit card, bank transfer, direct debit, etc. Return NONE if unspecified. "
            "Format: {'payment_method': 'credit_card', 'confidence': 8}. Example: {'payment_method': 'bank_transfer', 'confidence': 6}",
        
            # Aspect 10: Temporal Context
            "Does the text reference time-sensitive terms (e.g., 'today', 'immediately', 'last week')? 1 (no) to 9 (yes). "
            "Format: {'temporal_context': 5}. Example: {'temporal_context': 7}"
        ],
        model="minicpm-v",
        api_key="sk-1234",
        base_url="http://192.168.0.101:11434/v1"
    )


if __name__ == "__main__":
    
    model = DimStringVectorization()
    tasks = mteb.get_tasks(tasks=["Banking77Classification"])
    evaluation = mteb.MTEB(tasks=tasks)
    evaluation.run(model)
    
    # print(asyncio.run(run("I am happy")))
    
    # for _ in range(10):
    #     print(model.encode(["I am happy", "I am sad"]))