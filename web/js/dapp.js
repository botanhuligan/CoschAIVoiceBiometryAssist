BN = BigNumber

// TODO: to other conf file
let infuraProjectAddress = "https://ropsten.infura.io/v3/"
let wsInfuraProjectAddress = 'wss://ropsten.infura.io/ws/v3/'
let smartContractAddress = ""
let testWallet = ""
let privKey = ""

// Check balance and connection
web3 = new Web3(infuraProjectAddress)
web3.eth.getBalance(testWallet)
  .then(d => console.log(new BN(d).div(new BN(1e18)).toString(10), "ETH", "in", testWallet))
  .catch(console.log)

let {Tx} = ethereumjs
let Buffer = ethereumjs.Buffer.Buffer
let ABI = [
	{
		"constant": false,
		"inputs": [
			{
				"name": "key_",
				"type": "string"
			},
			{
				"name": "value_",
				"type": "string"
			}
		],
		"name": "add",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "key_",
				"type": "string"
			}
		],
		"name": "getByKey",
		"outputs": [
			{
				"name": "value_",
				"type": "string"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]


function addKeyValue(key_, value_){
	  return new Promise(async (resolve, reject) => {

	// not working with infura
    //contract.methods.add(key_, value_).send({ from: _from})

	 webSocketProvider = new Web3.providers.WebsocketProvider(wsInfuraProjectAddress);
	 web3 = new Web3(webSocketProvider);
	
	let _from = Wallet.fromPrivateKey(privKey).getChecksumAddressString()
	console.log(`Try connect contract`)
    let contract = new web3.eth.Contract(ABI, smartContractAddress, {from: _from})
	console.log(`Connect contract OK`)

		const query = contract.methods.add(key_, value_);
		const encodedABI = query.encodeABI();
		const tx = {
		  from: testWallet,
		  to: smartContractAddress,
		  gas: 2000000,
		  data: encodedABI,
		};
		console.log('transaction: '+JSON.stringify(tx))

		let dryPrivKey = "0x"+privKey

		web3.eth.accounts.signTransaction(tx, dryPrivKey).then(signed => {
		  const tran = web3.eth
		    .sendSignedTransaction(signed.rawTransaction)
		    .on('confirmation', (confirmationNumber, receipt) => {
		      console.log('=> confirmation: ' + confirmationNumber);
		    })
		    .on('transactionHash', hash => {
		      console.log('=> hash add transaction');
		      console.log(hash);
		    })
		    .on('receipt', receipt => {
		      console.log('=> reciept add transaction');
		      console.log(receipt);
		    })
		    .on('error', console.error);
		});


    console.log(`Add new pair`)

    value_ = await contract.methods.getByKey(key_).call()
    console.log(`Get value: `+value_)

    return resolve(value_) 
  })
}


function getValue(key_){
	  return new Promise(async (resolve, reject) => {
	console.log(`Start getValue`)

	web3 = new Web3(infuraProjectAddress)

    let _from = Wallet.fromPrivateKey(privKey).getChecksumAddressString()

 	console.log(`Try connect contract`)
    let contract = new web3.eth.Contract(ABI, smartContractAddress, {from: _from})
	console.log(`Connect contract OK`)

    let value_ = await contract.methods.getByKey(key_).call()
    console.log(`Get value: `+value_)

    return resolve(value_) 
  })
}